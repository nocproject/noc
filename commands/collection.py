# ----------------------------------------------------------------------
# Collections manipulation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import argparse

# Third-party modules
import orjson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.collection.base import Collection
from noc.core.fileutils import safe_rewrite
from noc.models import COLLECTIONS, get_model
from noc.core.mongo.connection import connect
from noc.models import is_document


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", help="sub-commands help", required=True)
        # sync
        subparsers.add_parser("sync", help="Synchronize collections")
        # install
        install_parser = subparsers.add_parser("install", help="Add collections to repository")
        install_parser.add_argument(
            "-r", "--remove", dest="remove", action="store_true", help="Remove installed files"
        )
        install_parser.add_argument(
            "-l", "--load", dest="load", action="store_true", help="Load to database"
        )
        install_parser.add_argument("install_files", nargs=argparse.REMAINDER, help="List of files")
        export_parser = subparsers.add_parser("export", help="Export collections")
        export_group_list = export_parser.add_argument_group("List arguments")
        export_group_list.add_argument(
            "-l",
            "--list-collections",
            dest="list_collection",
            metavar="collection_name",
            const=True,
            nargs="?",
            help="Show collection names /or list model in [collection_name]",
        )
        export_group_exp = export_parser.add_argument_group("Export arguments")
        export_group_exp.add_argument(
            "-p",
            "--path",
            dest="export_path",
            metavar="export_directory",
            help="Path for save exported collections",
        )
        export_group_exp.add_argument(
            "-c",
            "--collections",
            dest="export_collections",
            nargs="+",
            metavar="collection-name",
            help="List of collection for export",
        )
        export_group_exp.add_argument(
            "-n",
            "--object-name",
            dest="export_model_names",
            metavar="object-name",
            nargs="+",
            help="Export model names",
        )
        export_group_exp.add_argument(
            "-u",
            "--object-uuid",
            dest="export_model_uuids",
            metavar="uuid",
            nargs="+",
            help="Export model uuids",
        )

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_sync(self):
        connect()
        for c in Collection.iter_collections():
            try:
                c.sync()
            except ValueError as e:
                self.die(str(e))

    def handle_install(self, install_files=None, remove=False, load=False):
        connect()
        install_files = install_files or []
        for fp in install_files:
            if not os.path.isfile(fp):
                self.die("File not found: %s" % fp)
            with open(fp) as f:
                data = orjson.loads(f.read())
            try:
                Collection.install(data)
                if load:
                    c = Collection(data["$collection"])
                    c.update_item(data)
            except ValueError as e:
                self.die("%s - %s" % (fp, (str(e))))
            if remove:
                os.unlink(fp)

    def handle_export(
        self,
        list_collection=False,
        export_path=None,
        export_collections=None,
        export_model_names=None,
        export_model_uuids=None,
    ):
        connect()
        MODELS = {}
        for c in COLLECTIONS:
            cm = get_model(c)
            if is_document(cm):
                cn = cm._meta["json_collection"]
            else:
                cn = cm._json_collection.get("json_collection")
            MODELS[cn] = cm
        if list_collection is not None:
            if list_collection is True:
                for c in Collection.iter_collections():
                    print("%s" % c.name, file=self.stdout)
            else:
                if list_collection not in MODELS:
                    print("Collection not found", file=self.stdout)
                    return
                objs = MODELS[list_collection].objects.all().order_by("name")
                for o in objs:
                    print('uuid:%s name:"%s"' % (o.uuid, o.name), file=self.stdout)
        else:
            if not export_path or not export_collections:
                return
            if not os.path.isdir(export_path):
                self.die("Path not found: %s" % export_path)

            for ecname in export_collections:
                if ecname not in MODELS:
                    print("Collection not found", file=self.stdout)
                    continue
                kwargs = {}
                if export_model_names:
                    kwargs["name__in"] = export_model_names
                elif export_model_uuids:
                    kwargs["uuid__in"] = export_model_uuids
                objs = MODELS[ecname].objects.filter(**kwargs).order_by("name")
                for o in objs:
                    path = os.path.join(export_path, ecname, o.get_json_path())
                    print('export "%s" to %s' % (getattr(o, "name", o), path), file=self.stdout)
                    safe_rewrite(path, o.to_json(), mode=0o644)


if __name__ == "__main__":
    Command().run()
