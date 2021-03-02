# ----------------------------------------------------------------------
# Extract/Transfer/Load commands
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse

# Third-party modules
import yaml
import orjson

# NOC modules
from noc.core.mongo.connection import connect
from noc.core.management.base import BaseCommand
from noc.main.models.remotesystem import RemoteSystem
from noc.core.etl.loader.chain import LoaderChain


class Command(BaseCommand):
    CONF = "etc/etl.yml"

    SUMMARY_MASK = "%20s | %8s | %8s | %8s\n"
    CONTROL_MESSAGE = """Summary of %s changes: %d, overload control number: %d\n"""

    def add_arguments(self, parser):
        parser.add_argument("--system", action="append", help="System to extract")
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # load command
        load_parser = subparsers.add_parser("load")
        load_parser.add_argument("system", help="Remote system name")
        load_parser.add_argument(
            "loaders", nargs=argparse.REMAINDER, help="List of extractor names"
        )
        # check command
        check_parser = subparsers.add_parser("check")
        check_parser.add_argument("system", help="Remote system name")
        # diff command
        diff_parser = subparsers.add_parser("diff")
        diff_parser.add_argument("system", help="Remote system name")
        diff_parser.add_argument(
            "--summary", action="store_true", default=False, help="Show only summary"
        )
        diff_parser.add_argument(
            "--control-default",
            action="store",
            type=int,
            default=0,
            help="Default control number in summary object",
        )
        diff_parser.add_argument(
            "--control-dict", type=str, help="Dictionary of control numbers in summary object"
        )
        diff_parser.add_argument("diffs", nargs=argparse.REMAINDER, help="List of extractor names")
        db_diff = subparsers.add_parser("db-diff", help="Compare ETL and database state")
        db_diff.add_argument("--extractor", required=False, default="managedobject")
        db_diff.add_argument("--fields", help="List fields for compare", required=False)
        db_diff.add_argument("system", help="Remote system name")
        # extract command
        extract_parser = subparsers.add_parser("extract")
        extract_parser.add_argument("system", help="Remote system name")
        extract_parser.add_argument(
            "quiet", action="store_true", default=False, help="Remote system name"
        )
        extract_parser.add_argument(
            "extractors", nargs=argparse.REMAINDER, help="List of extractor names"
        )

    def get_config(self):
        with open(self.CONF) as f:
            return yaml.safe_load(f)

    def handle(self, cmd, *args, **options):
        connect()
        return getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    def handle_load(self, *args, **options):
        remote_system = RemoteSystem.get_by_name(options["system"])
        if not remote_system:
            self.die("Invalid remote system: %s" % options["system"])
        remote_system.load(options.get("loaders", []), quiet=options.get("quiet", False))

    def handle_extract(self, *args, **options):
        remote_system = RemoteSystem.get_by_name(options["system"])
        if not remote_system:
            self.die("Invalid remote system: %s" % options["system"])
        remote_system.extract(options.get("extractors", []), quiet=options.get("quiet", False))

    def handle_check(self, *args, **options):
        remote_system = RemoteSystem.get_by_name(options["system"])
        if not remote_system:
            self.die("Invalid remote system: %s" % options["system"])
        n_errors = remote_system.check(self.stdout)
        return 1 if n_errors else 0

    def handle_diff(self, summary=False, *args, **options):
        remote_system = RemoteSystem.get_by_name(options["system"])
        if not remote_system:
            self.die("Invalid remote system: %s" % options["system"])

        diffs = set(options.get("diffs", []))
        if summary:
            self.stdout.write(self.SUMMARY_MASK % ("Loader", "New", "Updated", "Deleted"))
        control_dict = {}
        if options["control_dict"]:
            try:
                control_dict = orjson.loads(options["control_dict"])
            except ValueError as e:
                self.die("Failed to parse JSON: %s in %s" % (e, options["control_dict"]))
            except TypeError as e:
                self.die("Failed to parse JSON: %s in %s" % (e, options["control_dict"]))
        chain = remote_system.get_loader_chain()
        for ldr in chain:
            if diffs and ldr.name not in diffs:
                continue
            if summary:
                i, u, d = ldr.check_diff_summary()
                control_num = control_dict.get(ldr.name, options["control_default"])
                self.stdout.write(self.SUMMARY_MASK % (ldr.name, i, u, d))
                if control_num:
                    if sum([i, u, d]) >= control_num:
                        self.stdout.write(
                            self.CONTROL_MESSAGE % (ldr.name, sum([i, u, d]), control_num)
                        )
                        self.stderr.write(
                            self.CONTROL_MESSAGE % (ldr.name, sum([i, u, d]), control_num)
                        )
                        n_errors = 1
                        break
            else:
                ldr.check_diff()
        else:
            n_errors = 0
        return 1 if n_errors else 0

    def iter_db(self, db_objects, model):
        for d in db_objects:
            d["id"] = d["remote_id"]
            # @todo Fix required fields, perhaps pyDantic alias
            if "object_profile_id" in d:
                d["object_profile"] = d["object_profile_id"]
            if "administrative_domain_id" in d:
                d["administrative_domain"] = d["administrative_domain_id"]
            yield model(**d)

    def handle_db_diff(self, *args, **options):
        from noc.sa.models.managedobject import ManagedObject

        remote_system = RemoteSystem.get_by_name(options["system"])
        if not remote_system:
            self.die("Invalid remote system: %s" % options["system"])
        loader = options["extractor"]
        include_fields = None
        if options.get("fields"):
            include_fields = set(options["fields"].split(","))
        chain = LoaderChain(remote_system)
        line = chain.get_loader(loader)
        ls = line.get_new_state()
        if not ls:
            ls = line.get_current_state()
        iter_db = line.model.objects.filter(remote_system=remote_system)
        deleted_filter = {}
        if line.model is ManagedObject:
            # On delete ManagedObject is set is_managed False
            self.print("Apply is_managed filter")
            deleted_filter = set(
                iter_db.filter(is_managed=False).values_list("remote_id", flat=True)
            )
            iter_db = iter_db.filter(is_managed=True)
        for o, n in line.diff(
            line.iter_jsonl(ls),
            self.iter_db(iter_db.values().order_by("remote_id"), line.data_model),
            include_fields=include_fields,
        ):
            if o is None and n:
                print("New:", n.id, n.name)
            elif o and n is None:
                if deleted_filter and o.id in deleted_filter:
                    continue
                print("Deleted:", o.id, o.name)
            else:
                print(
                    "Changed:",
                    o.id,
                    o.name,
                    o.dict(include=include_fields),
                    n.dict(include=include_fields),
                )


if __name__ == "__main__":
    Command().run()
