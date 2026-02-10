# ----------------------------------------------------------------------
# Beef management
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import datetime
import os
import re
import codecs

# Third-party modules
import uuid
import yaml
import orjson

# NOC modules
from noc.core.mongo.connection import connect
from noc.core.management.base import BaseCommand
from noc.core.script.beef import Beef
from noc.main.models.extstorage import ExtStorage
from noc.core.comp import smart_text, smart_bytes
from noc.core.ioloop.util import setup_asyncio


class Command(BaseCommand):
    CLI_ENCODING = "quopri"
    DEFAULT_BEEF_PATH_TEMPLATE = "ad-hoc/{0.profile.name}/{0.pool.name}/{0.address}.beef.json.bz2"
    DEFAULT_BEEF_IMPORT_PATH_TEMPLATE = "imports/{0.box.profile}/{0.uuid}.beef.json.bz2"
    DEFAULT_TEST_CASE_TEMPLATE = "ad-hoc/{0.profile.name}/{0.uuid}/"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # collect command
        collect_parser = subparsers.add_parser("collect")
        collect_parser.add_argument("--spec", help="Spec path or URL")
        collect_parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Ignore beef policy setings in ManagedObject",
        )
        collect_parser.add_argument("--storage", help="External storage name or url")
        collect_parser.add_argument("--path", type=smart_text, help="Path name")
        collect_parser.add_argument("--description", type=smart_text, help="Set beef description")
        collect_parser.add_argument("objects", nargs=argparse.REMAINDER, help="Object names or ids")
        # view command
        view_parser = subparsers.add_parser("view")
        view_parser.add_argument("--storage", help="External storage name or url")
        view_parser.add_argument("--path", type=smart_text, help="Beef UUID or path name")
        # edit command
        export_parser = subparsers.add_parser("export")
        export_parser.add_argument("--storage", help="External storage name or url")
        export_parser.add_argument("--path", type=smart_text, help="Beef UUID or path name")
        export_parser.add_argument("--export-path", help="Path file for export")
        # edit command
        import_parser = subparsers.add_parser("import")
        import_parser.add_argument("--storage", help="External storage name or url")
        import_parser.add_argument("--path", type=smart_text, help="Path name")
        import_parser.add_argument("paths", nargs=argparse.REMAINDER, help="Path to imported beef")
        # list command
        list_parser = subparsers.add_parser("list")  # noqa
        list_parser.add_argument("--storage", help="External storage name or url")
        list_parser.add_argument("--path", type=smart_text, help="Beef UUID or path name")
        # test command
        run_parser = subparsers.add_parser("run")
        run_parser.add_argument(
            "--script", action="append", help="Script name for runs. Default (get_version)"
        )
        run_parser.add_argument("--storage", help="External storage name")
        run_parser.add_argument("--path", type=smart_text, help="Beef UUID or path name")
        run_parser.add_argument("--access-preference", default="CS", help="Access preference")
        out_group = run_parser.add_mutually_exclusive_group()
        out_group.add_argument(
            "--pretty",
            action="store_true",
            dest="pretty",
            default=False,
            help="Pretty-print output",
        )
        out_group.add_argument(
            "--yaml", action="store_true", dest="yaml", default=False, help="YAML output"
        )
        run_parser.add_argument("arguments", nargs=argparse.REMAINDER, help="Script arguments")
        # create-test-case
        create_test_case_parser = subparsers.add_parser("create-test-case")
        create_test_case_parser.add_argument("--storage", help="External storage name")
        create_test_case_parser.add_argument("--path", type=smart_text, help="Path name")
        create_test_case_parser.add_argument("--test-storage", help="External storage name")
        create_test_case_parser.add_argument("--test-path", type=smart_text, help="Path name")
        create_test_case_parser.add_argument("--config-storage", help="External storage name")
        create_test_case_parser.add_argument(
            "--config-path", type=smart_text, default="/", help="Path name"
        )
        create_test_case_parser.add_argument(
            "--build", action="store_true", default=False, help="Build test case after create"
        )
        # build-test-case
        build_test_case_parser = subparsers.add_parser("build-test-case")
        build_test_case_parser.add_argument("--test-storage", help="External storage name")
        build_test_case_parser.add_argument("--test-path", type=smart_text, help="Path name")

    def handle(self, cmd, *args, **options):
        setup_asyncio()
        # Normalize to the function name
        n_cmd = cmd.replace("-", "_")
        # Run handler
        return getattr(self, f"handle_{n_cmd}")(*args, **options)

    def handle_collect(
        self, storage, path, spec, force, objects, description=None, *args, **options
    ):
        connect()
        from noc.inv.models.resourcegroup import ResourceGroup
        from noc.dev.models.spec import Spec
        from fs import open_fs

        class FakeSpec(object):
            def __init__(self, name):
                self.name = name
                self.uuid = "4ec10fd8-3a33-4f23-b96e-91e3967c3b1b"

        # Get spec data
        if ":" in spec:
            path, file = smart_text(os.path.dirname(spec)), smart_text(os.path.basename(spec))
            spec_data = open_fs(path).open(file)
            sp = Spec.from_json(spec_data.read())
            sp.quiz = FakeSpec("Ad-Hoc")
            sp.profile = FakeSpec("Generic.Host")
        else:
            sp = Spec.get_by_name(spec)
        if not sp:
            self.die(f"Invalid spec: '{spec}'")
        # Spec data
        req = sp.get_spec_request()
        # Get effective list of managed objects
        mos = set()
        for ox in objects:
            for mo in ResourceGroup.get_objects_from_expression(ox, model_id="sa.ManagedObject"):
                mos.add(mo)
        # Collect beefs
        for mo in mos:
            self.print(f"Collecting beef from {mo.name}")
            if ":" in spec:
                sp.profile = mo.profile
            if mo.profile.name != sp.profile.name:
                self.print("  Profile mismatch. Skipping")
                continue
            if mo.object_profile.beef_policy == "D" and not force:
                self.print("  Collection disabled by policy. Skipping")
                continue
            if not mo.object_profile.beef_storage and not storage:
                self.print("  Beef storage is not configured. Skipping")
                continue
            if not mo.object_profile.beef_path_template and not force:
                self.print("  Beef path template is not configured. Skipping")
                continue
            if not mo.object_profile.beef_path_template and force:
                self.print("  Beef path template is not configured. But force set. Generate path")
                path = smart_text(self.DEFAULT_BEEF_PATH_TEMPLATE.format(mo))
            else:
                path = smart_text(
                    mo.object_profile.beef_path_template.render_subject(
                        object=mo, spec=sp, datetime=datetime
                    )
                )
            storage = mo.object_profile.beef_storage or self.get_storage(storage, beef=True)
            if not path:
                self.print("  Beef path is empty. Skipping")
                continue
            try:
                bdata = mo.scripts.get_beef(spec=req)
            except Exception as e:
                self.print(f"Failed collect beef on {mo.name}: {e}")
                continue
            beef = Beef.from_json(bdata)
            if description:
                beef.description = description
            self.print(f"  Saving to {storage.name}:{path}")
            try:
                cdata, udata = beef.save(storage, path)
                if cdata == udata:
                    self.print(f"  {cdata} bytes written")
                else:
                    ratio = float(udata) / float(cdata)
                    self.print(
                        f"  {cdata} bytes written ({udata} uncompressed. Ratio {ratio:.2f}/1)"
                    )
            except IOError as e:
                self.print(f"  Failed to save: {e}")
            self.print("  Done")

    def handle_view(self, storage, path=None, *args, **options):
        st = self.get_storage(storage, beef=True)
        beef = self.beef_filter(st, path)
        if beef:
            beef, _ = beef[0]
        else:
            self.die(f"Beef not found: {path}")
        r = [
            f"UUID     : {beef.uuid}",
            f"Profile  : {beef.box.profile}",
            f"Platform : {beef.box.vendor} {beef.box.platform} Version: {beef.box.version}",
            f"Spec     : {beef.spec}",
            f"Changed  : {beef.changed}",
        ]
        r += ["Description:\n  %s\n" % beef.description.replace("\n", "\n  ")]
        r += ["--[CLI FSM]----------"]
        for c in beef.cli_fsm:
            r += [f"---- State: {c.state}"]
            for n, reply in enumerate(c.reply):
                r += [f"-------- Packet #{n}", f"{beef._cli_decoder(reply)!r}"]
        r += ["--[CLI]----------"]
        for c in beef.cli:
            r += [f"---- Names: {', '.join(c.names)}"]
            r += [f"-------- Request: {c.request!r}"]
            for n, reply in enumerate(c.reply):
                r += [f"-------- Packet #{n}", f"{beef._cli_decoder(reply)!r}"]
        # Dump output
        self.stdout.write("\n".join(r) + "\n")

    def handle_export(self, storage, path, export_path=None, *args, **options):
        """
        Export Beef to yaml file
        :param storage:
        :param path:
        :param export_path:
        :return:
        """
        st = self.get_storage(storage, beef=True)
        beef = self.beef_filter(st, path)
        if beef:
            beef, _ = beef[0]
        else:
            self.die(f"Beef not found: {path}")
        # beef = self.get_beef(st, path)
        data = beef.get_data(decode=True)
        if not export_path:
            self.print(yaml.dump(data))
        else:
            with open(export_path, "w") as f:
                f.write(yaml.dump(data))

    def handle_import(self, storage, path=None, paths=None, *args, **options):
        """
        Importing yaml file to beef
        :param storage:
        :param path:
        :param paths:
        :return:
        """
        for import_path in paths:
            self.print(f"Importing {import_path} ...")
            with open(import_path, "r") as f:
                data = yaml.safe_load(f)
            for c in data["cli_fsm"]:
                c["reply"] = [
                    codecs.encode(smart_bytes(reply), self.CLI_ENCODING) for reply in c["reply"]
                ]
            for c in data["cli"]:
                c["reply"] = [
                    codecs.encode(smart_bytes(reply), self.CLI_ENCODING) for reply in c["reply"]
                ]
            for m in data["mib"]:
                m["value"] = codecs.encode(smart_bytes(m["value"]), self.CLI_ENCODING)
            try:
                beef = Beef.from_json(data)
            except ValueError:
                self.print(f"Error when importing beef file {import_path}")
                continue
            st = self.get_storage(storage, beef=True)
            if not path:
                path = smart_text(self.DEFAULT_BEEF_IMPORT_PATH_TEMPLATE.format(beef))
            beef.save(st, smart_text(path))

    def handle_list(self, storage=None, *args, **options):
        if storage:
            storages = [self.get_storage(name=storage)]
        else:
            connect()
            storages = ExtStorage.objects.filter(type="beef")
        for storage in storages:
            self.print(f"\n{'=' * 20}Storage: {storage.name}{'=' * 20}\n")
            r = ["GUID,Profile,Vendor,Platform,Version,Description,SpecUUID,Changed,Path"]
            st_fs = storage.open_fs()
            for step in st_fs.walk("", exclude=["*.yml"]):
                if not step.files:
                    continue
                for file in step.files:
                    try:
                        beef = Beef.load(storage, file.make_path(step.path))
                    except ValueError:
                        self.print(f"Error when loading beef file {file.make_path(step.path)}")
                        continue
                    r += [
                        ",".join(
                            [
                                beef.uuid,
                                beef.box.profile,
                                beef.box.vendor,
                                beef.box.platform,
                                beef.box.version,
                                beef.description,
                                beef.spec or "",  # For ad-hoc specs
                                beef.changed,
                                file.make_path(step.path),
                            ]
                        )
                    ]
            # Dump output
            self.stdout.write("\n".join(r) + "\n")

    def handle_run(
        self,
        path,
        storage,
        script,
        pretty=False,
        yaml=False,
        access_preference="SC",
        arguments=None,
        *args,
        **options,
    ):
        from noc.core.script.loader import loader

        if not path:
            self.die("Set Path or UUID")
        st = self.get_storage(storage, beef=True)
        # beef = self.get_beef(st, path)
        beef = self.beef_filter(st, path)
        if beef:
            beef, _ = beef[0]
        else:
            self.die(f"Beef path {path} not found")
        # Build credentials
        credentials = {
            "address": beef.uuid,
            "cli_protocol": "beef",
            "beef_storage_url": st.url,
            "beef_path": beef._path,
            "access_preference": access_preference,
            "snmp_ro": "public",
        }
        # Get capabilities
        caps = {}
        # Parse arguments
        script_args = self.get_script_args(arguments or [])
        # Run script
        service = ServiceStub(pool="default")
        for s_name in script:
            if "." not in script:
                s_name = f"{beef.box.profile}.{s_name}"
            scls = loader.get_script(s_name)
            if not scls:
                self.die(f"Failed to load script '{script}'")
            scr = scls(
                service=service,
                credentials=credentials,
                capabilities=caps,
                version={
                    "vendor": beef.box.vendor,
                    "platform": beef.box.platform,
                    "version": beef.box.version,
                },
                timeout=3600,
                name=s_name,
                args=script_args,
            )
            result = scr.run()
            if pretty:
                import pprint

                pprint.pprint(result)
            elif yaml:
                import yaml
                import sys

                yaml.dump(result, sys.stdout, indent=2)
            else:
                self.stdout.write(f"{result}\n")

    def handle_create_test_case(
        self,
        storage=None,
        path=None,
        config_storage=None,
        config_path=None,
        test_storage=None,
        test_path=None,
        build=False,
        *args,
        **options,
    ):
        beef_storage = self.get_storage(storage)
        # Load beef
        beefs = self.beef_filter(storage=beef_storage, path=path, with_tests=True)
        # Load config
        cfg = None
        if config_storage and config_path:
            cfg = self.get_config(config_storage, config_path)
        # Create test
        test_storage = self.get_storage(test_storage, beef_test=True)
        with test_storage.open_fs() as fs:
            # Load beef
            for beef, t_config in beefs:
                # beef, t_config = beefs[(storage, path)]
                config = cfg or t_config
                # Create test directory
                save_path = test_path or beef._path
                if fs.exists(save_path):
                    self.print(f"Path {save_path} already exists. Skipping...")
                    continue
                self.print(f"Creating {test_storage}:{save_path}")
                fs.makedirs(smart_text(save_path))
                # Write config
                # config = cfg[beef.uuid][0] if beef.uuid in cfg else cfg[""][0]
                config["beef"] = str(beef.uuid)
                self.print(f"Writing {test_storage}:{save_path}/test-config.yml")
                fs.writebytes(
                    smart_text(os.path.join(save_path, "test-config.yml")),
                    smart_bytes(yaml.dump(config, default_flow_style=False)),
                )
                # Write beef
                self.print(f"Writing {test_storage}:{save_path}/beef.json.bz2")
                beef.save(test_storage, smart_text(os.path.join(save_path, "beef.json.bz2")))
                if build:
                    self.handle_build_test_case(test_storage, save_path)

    def handle_build_test_case(self, test_storage, test_path, cfg=None, *args, **options):
        import bz2
        from noc.core.script.loader import loader

        if isinstance(test_storage, str):
            test_st = self.get_storage(test_storage, beef_test=True)
        else:
            test_st = test_storage
        if not cfg:
            # Get config
            with test_st.open_fs() as fs:
                data = fs.readbytes(smart_text(os.path.join(test_path, "test-config.yml")))
                cfg = yaml.safe_load(data)
        # Get beef
        beef_path = os.path.join(test_path, "beef.json.bz2")
        beef = self.get_beef(test_st, beef_path)
        # Get capabilities
        caps = {}
        # Run tests
        tests = cfg.get("tests", [])
        service = ServiceStub(pool="default")
        for n, test in enumerate(tests):
            # Load script
            script = f"{beef.box.profile}.{test['script']}"
            scls = loader.get_script(script)
            if not scls:
                self.die(f"Failed to load script '{script}'")
            # Build credentials
            credentials = {
                "address": beef.uuid,
                "cli_protocol": "beef",
                "beef_storage_url": test_st.url,
                "beef_path": beef_path,
                "access_preference": test.get("access_preference", "SC"),
            }
            # Build version
            version = {
                "vendor": beef.box.vendor,
                "platform": beef.box.platform,
                "version": beef.box.version,
            }
            # @todo: Input
            scr = scls(
                service=service,
                credentials=credentials,
                capabilities=caps,
                version=version,
                timeout=3600,
                name=script,
            )
            self.print(f"[{n:04d}] Running {test['script']}")
            result = scr.run()
            tc = {
                "script": script,
                "capabilities": caps,
                "credentials": credentials,
                "version": version,
                "input": {},
                "result": result,
            }
            data = bz2.compress(orjson.dumps(tc))
            rn = os.path.join(test_path, f"{n:04d}.{test['script']}.json.bz2")
            self.print(f"[{n:04d}] Writing {rn}")
            with test_st.open_fs() as fs:
                fs.writebytes(smart_text(rn), data)

    def get_storage(self, name, beef=False, beef_test=False, beef_test_config=False):
        """
        Get beef storage by name
        :param name:
        :type name: str
        :param beef:
        :type beef: bool
        :param beef_test:
        :type beef_test: bool
        :param beef_test_config:
        :type beef_test_config: bool
        :return:
        :rtype: ExtStorage
        """
        beef_type = "beef"
        if beef_test:
            beef_type = "beef_test"
        elif beef_test_config:
            beef_type = "beef_test_config"
        if not name:
            self.die(f"Unknown storage: {name}")
        if ":" in name:
            # URL
            st = ExtStorage.from_json(f'{"name": "local", "url": "{name}", "type": "{beef_type}"}')
        else:
            connect()
            st = ExtStorage.get_by_name(name)
        if not st:
            self.die(f"Invalid storage: {name}")
        if st.type != beef_type:
            self.die(f"Storage is not configured for {beef_type}")
        return st

    def get_beef(self, storage, path):
        """
        Get beef
        :param storage: Storage instance
        :param path: Beef path
        :return:
        """
        try:
            return Beef.load(storage, path)
        except IOError as e:
            self.die(f"Failed to load beef: {e}")

    def get_config(self, storage=None, path=None):
        config_st = self.get_storage(storage, beef_test_config=True)
        with config_st.open_fs() as fs:
            cfg = fs.readbytes(smart_text(path))
            return yaml.safe_load(cfg)

    def beef_filter(self, storage=None, path="/", uuids=None, profile=None, with_tests=False):
        """
        Get beef storage by name
        :param storage:
        :param path:
        :param uuids:
        :param profile:
        :param with_tests:
        :return:
        :rtype: list
        """
        test_config = {}
        try:
            uuids = [str(uuid.UUID(path))]
            path = "/"
        except ValueError:
            pass
        if with_tests:
            test_config = self.get_test_configs(storage)
            self.print("Configs for tests %s", test_config)
        r = []
        st_fs = storage.open_fs()
        file_filter = []
        if st_fs.isfile(path):
            file_filter = [os.path.basename(path)]
            path = os.path.dirname(path)
        for beef_path in st_fs.walk.files(
            path=smart_text(path), exclude=["*.yml"], filter=file_filter
        ):
            try:
                beef = self.get_beef(storage, beef_path)
            except ValueError:
                self.print(f"Bad beef on path {beef_path}")
                continue
            if uuids and beef.uuid not in uuids:
                continue
            if profile and beef.profile != "profile":
                continue
            if test_config and beef.uuid in test_config:
                tc = test_config[beef.uuid]
            elif test_config and os.path.dirname(beef_path) in test_config:
                tc = test_config[os.path.dirname(beef_path)]
            else:
                tc = None
            # r[(st_fs, beef_path)] = (beef, tc)
            beef._path = beef_path
            r += [(beef, tc)]
        return r

    def get_test_configs(self, storage):
        """
        Getting test config from beef folder
        * base config - first yaml
        * if config has beef uuid - config for beef

        """
        r = {}
        with storage.open_fs() as fs:
            r["/"] = yaml.safe_load(fs.readbytes("test-config.yml"))
            for step in fs.walk.walk(filter=["*.yml"]):
                for f in step.files:
                    data = yaml.safe_load(fs.readbytes(os.path.join(step.path, f.name)))
                    r[data.get("beef", step.path)] = data
                if not step.files:
                    base_path = list(os.path.split(step.path))
                    while base_path:
                        path = os.path.join(*base_path)
                        if path in r:
                            r[step.path] = r[path]
                            break
                        base_path.pop()
                    if step.path not in r:
                        # default
                        r[step.path] = r["/"]
        return r

    rx_arg = re.compile(r"^(?P<name>[a-zA-Z][a-zA-Z0-9_]*)(?P<op>:?=@?)(?P<value>.*)$")

    def get_script_args(self, arguments):
        """
        Parse arguments and return script's
        """

        def read_file(path):
            if not os.path.exists(path):
                self.die(f"Cannot open file '{path}'")
            with open(path) as f:
                return f.read()

        def parse_json(j):
            try:
                return orjson.loads(j)
            except ValueError as e:
                self.die(f"Failed to parse JSON: {e}")

        args = {}
        for a in arguments:
            match = self.rx_arg.match(a)
            if not match:
                self.die(f"Malformed parameter: '{a}'")
            name, op, value = match.groups()
            if op == "=":
                # Set parameter
                args[name] = value
            elif op == "=@":
                # Read from file
                args[name] = read_file(value)
            elif op == ":=":
                # Set to JSON value
                args[name] = parse_json(value)
            elif op == ":=@":
                # Set to JSON value from a file
                args[name] = parse_json(read_file(value))
        return args


class ServiceStub(object):
    class ServiceConfig(object):
        def __init__(self, pool, tos=None):
            self.pool = pool
            self.tos = tos

    def __init__(self, pool):
        self.config = self.ServiceConfig(pool=pool)


if __name__ == "__main__":
    Command().run()
