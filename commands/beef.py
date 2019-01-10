# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Beef management
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import argparse
import datetime
import os
import re
from collections import defaultdict
# Third-party modules
import six
import ujson
import yaml
# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.script.beef import Beef
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.dev.models.spec import Spec
from noc.main.models.extstorage import ExtStorage


class Command(BaseCommand):
    CLI_ENCODING = "quopri"
    MIB_ENCODING = "base64"
    DEFAULT_BEEF_PATH_TEMPLATE = u"ad-hoc/{0.profile.name}/{0.pool.name}/{0.address}.beef.json"
    DEFAULT_TEST_CASE_TEMPLATE = u"ad-hoc/{0.profile.name}/{0.uuid}/"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # collect command
        collect_parser = subparsers.add_parser("collect")
        collect_parser.add_argument(
            "--spec",
            help="Spec path or URL"
        )
        collect_parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Ignore beef policy setings in ManagedObject"
        )
        collect_parser.add_argument(
            "--storage",
            help="External storage name"
        )
        collect_parser.add_argument(
            "--path",
            help="Path name"
        )
        collect_parser.add_argument(
            "objects",
            nargs=argparse.REMAINDER,
            help="Object names or ids"
        )
        # view command
        view_parser = subparsers.add_parser("view")
        view_parser.add_argument(
            "--storage",
            help="External storage name"
        )
        view_parser.add_argument(
            "--path",
            help="Path name"
        )
        # edit command
        export_parser = subparsers.add_parser("export")
        export_parser.add_argument(
            "--storage",
            help="External storage name"
        )
        export_parser.add_argument(
            "--path",
            help="Path name"
        )
        export_parser.add_argument(
            "--export-path",
            help="Path file for export"
        )
        # edit command
        import_parser = subparsers.add_parser("import")
        import_parser.add_argument(
            "--storage",
            help="External storage name"
        )
        import_parser.add_argument(
            "--path",
            help="Path name"
        )
        import_parser.add_argument(
            "paths",
            nargs=argparse.REMAINDER,
            help="Path to imported beef"
        )
        # list command
        list_parser = subparsers.add_parser("list")  # noqa
        list_parser.add_argument(
            "--storage",
            help="External storage name"
        )
        list_parser.add_argument(
            "--path",
            help="Path name"
        )
        # test command
        run_parser = subparsers.add_parser("run")
        run_parser.add_argument(
            "--script",
            action="append",
            help="Script name for runs. Default (get_version)"
        )
        run_parser.add_argument(
            "--storage",
            help="External storage name"
        )
        run_parser.add_argument(
            "--path",
            help="Path name"
        )
        run_parser.add_argument(
            "--access-preference",
            help="Access preference"
        )
        out_group = run_parser.add_mutually_exclusive_group()
        out_group.add_argument(
            "--pretty",
            action="store_true",
            dest="pretty",
            default=False,
            help="Pretty-print output"
        )
        out_group.add_argument(
            "--yaml",
            action="store_true",
            dest="yaml",
            default=False,
            help="YAML output"
        )
        run_parser.add_argument(
            "arguments",
            nargs=argparse.REMAINDER,
            help="Script arguments"
        )
        # create-test-case
        create_test_case_parser = subparsers.add_parser("create-test-case")
        create_test_case_parser.add_argument(
            "--storage",
            help="External storage name"
        )
        create_test_case_parser.add_argument(
            "--path",
            help="Path name"
        )
        create_test_case_parser.add_argument(
            "--test-storage",
            help="External storage name"
        )
        create_test_case_parser.add_argument(
            "--test-path",
            help="Path name"
        )
        create_test_case_parser.add_argument(
            "--config-storage",
            help="External storage name"
        )
        create_test_case_parser.add_argument(
            "--config-path",
            help="Path name"
        )
        create_test_case_parser.add_argument(
            "--build",
            action="store_true",
            default=False,
            help="Build test case after create"
        )
        # build-test-case
        build_test_case_parser = subparsers.add_parser("build-test-case")
        build_test_case_parser.add_argument(
            "--test-storage",
            help="External storage name"
        )
        build_test_case_parser.add_argument(
            "--test-path",
            help="Path name"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd.replace("-", "_"))(*args, **options)

    def handle_collect(self, storage, path, spec, force, objects, *args, **options):
        # Get spec data
        sp = Spec.get_by_name(spec)
        if not sp:
            self.die("Invalid spec: '%s'" % spec)
        # Spec data
        req = sp.get_spec_request()
        # Get effective list of managed objects
        mos = set()
        for ox in objects:
            for mo in ManagedObjectSelector.resolve_expression(ox):
                mos.add(mo)
        # Collect beefs
        for mo in mos:
            self.print("Collecting beef from %s" % mo.name)
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
            elif not mo.object_profile.beef_path_template and force:
                self.print("  Beef path template is not configured. But force set. Generate path")
                path = self.DEFAULT_BEEF_PATH_TEMPLATE.format(mo)
            else:
                path = mo.object_profile.beef_path_template.render_subject(
                    object=mo,
                    spec=sp,
                    datetime=datetime
                )
            storage = mo.object_profile.beef_storage or self.get_storage(storage, beef=True)
            if not path:
                self.print("  Beef path is empty. Skipping")
                continue
            try:
                bdata = mo.scripts.get_beef(spec=req)
            except Exception as e:
                self.print("Failed collect beef on %s: %s" % (mo.name, e))
                continue
            beef = Beef.from_json(bdata)
            self.print("  Saving to %s:%s" % (storage.name, path))
            try:
                cdata, udata = beef.save(storage, path)
                if cdata == udata:
                    self.print("  %d bytes written" % cdata)
                else:
                    self.print("  %d bytes written (%d uncompressed. Ratio %.2f/1)" % (
                        cdata, udata, float(udata) / float(cdata)))
            except IOError as e:
                self.print("  Failed to save: %s" % e)
            self.print("  Done")

    def handle_view(self, storage, path, *args, **options):
        st = self.get_storage(storage, beef=True)
        beef = self.get_beef(st, path)
        r = [
            "UUID     : %s" % beef.uuid,
            "Profile  : %s" % beef.box.profile,
            "Platform : %s %s Version: %s" % (
                beef.box.vendor,
                beef.box.platform,
                beef.box.version
            ),
            "Spec     : %s" % beef.spec,
            "Changed  : %s" % beef.changed
        ]
        if True or beef.description:
            r += ["Description:\n  %s\n" % beef.description.replace("\n", "\n  ")]
        r += ["--[CLI FSM]----------"]
        for c in beef.cli_fsm:
            r += ["---- State: %s" % c.state]
            for n, reply in enumerate(c.reply):
                r += [
                    "-------- Packet #%d" % n,
                    "%r" % beef._cli_decoder(reply)
                ]
        r += ["--[CLI]----------"]
        for c in beef.cli:
            r += ["---- Names: %s" % ", ".join(c.names)]
            r += ["-------- Request: %r" % c.request]
            for n, reply in enumerate(c.reply):
                r += [
                    "-------- Packet #%d" % n,
                    "%r" % beef._cli_decoder(reply)
                ]
        # Dump output
        self.stdout.write("\n".join(r) + "\n")
        return

    def handle_export(self, storage, path, export_path=None, *args, **options):
        """
        Export Beef to yaml file
        :param storage:
        :param path:
        :param export_path:
        :return:
        """
        st = self.get_storage(storage, beef=True)
        beef = self.get_beef(st, path)
        data = beef.get_data()
        for c in data["cli_fsm"]:
            c["reply"] = [beef._cli_decoder(reply) for reply in c["reply"]]
        for c in data["cli"]:
            c["reply"] = [beef._cli_decoder(reply) for reply in c["reply"]]
        for m in data["mib"]:
            m["value"] = beef._mib_decoder(m["value"])
        if not export_path:
            self.print(yaml.dump(data))
        else:
            with open(export_path, "w") as f:
                f.write(yaml.dump(data))

    def handle_import(self, storage, path, paths=None, *args, **options):
        """
        Importing yaml file to beef
        :param storage:
        :param path:
        :param paths:
        :return:
        """
        for import_path in paths:
            self.print("Importing %s ..." % import_path)
            with open(import_path, "r") as f:
                data = yaml.load(f)
            for c in data["cli_fsm"]:
                c["reply"] = [reply.encode(self.CLI_ENCODING) for reply in c["reply"]]
            for c in data["cli"]:
                c["reply"] = [reply.encode(self.CLI_ENCODING) for reply in c["reply"]]
            for m in data["mib"]:
                m["value"] = m["value"].encode(self.CLI_ENCODING)
            beef = Beef.from_json(data)
            st = self.get_storage(storage, beef=True)
            beef.save(st, unicode(path))

    def handle_list(self, storage=None, *args, **options):
        r = ["GUID,Profile,Vendor,Platform,Version,SpecUUID,Changed,Path"]
        for storage in self.iter_storage(name=storage, beef=True):
            self.print("\n%sStorage: %s%s\n" % ("=" * 20, storage.name, "=" * 20))
            st_fs = storage.open_fs()
            for step in st_fs.walk(''):
                if not step.files:
                    continue
                for file in step.files:
                    beef = Beef.load(storage, file.make_path(step.path))
                    r += [",".join([
                        beef.uuid,
                        beef.box.profile,
                        beef.box.vendor,
                        beef.box.platform,
                        beef.box.version,
                        beef.spec,
                        beef.changed,
                        file.make_path(step.path)
                    ])]
            # Dump output
            self.stdout.write("\n".join(r) + "\n")
        return

    def handle_run(self, path, storage, script, pretty=False, yaml=False, access_preference="SC",
                   arguments=None, *args, **options):
        from noc.core.script.loader import loader
        st = self.get_storage(storage, beef=True)
        beef = self.get_beef(st, path)
        # Build credentials
        credentials = {
            "address": beef.uuid,
            "cli_protocol": "beef",
            "beef_storage_url": st.url,
            "beef_path": path,
            "access_preference": access_preference,
            "snmp_ro": "public"
        }
        # Get capabilities
        caps = {}
        # Parse arguments
        script_args = self.get_script_args(arguments or [])
        # Run script
        service = ServiceStub(pool="default")
        for s_name in script:
            if "." not in script:
                s_name = "%s.%s" % (beef.box.profile, s_name)
            scls = loader.get_script(s_name)
            if not scls:
                self.die("Failed to load script '%s'" % script)
            scr = scls(
                service=service,
                credentials=credentials,
                capabilities=caps,
                version={
                    "vendor": beef.box.vendor,
                    "platform": beef.box.platform,
                    "version": beef.box.version
                },
                timeout=3600,
                name=s_name,
                args=script_args
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
                self.stdout.write("%s\n" % result)

    def handle_create_test_case(self, storage=None, path=None, config_storage=None, config_path=None,
                                test_storage=None, test_path=None, build=False, *args, **options):
        # Load beef
        beefs = self.get_beefs(storage=storage, path=path)
        # Load config
        cfg = self.get_config(config_storage, config_path)
        # Create test
        test_storage = next(self.iter_storage(test_storage, beef_test=True))
        with test_storage.open_fs() as fs:
            # Load beef
            for (storage, path), beef in six.iteritems(beefs):
                # Create test directory
                save_path = test_path or path
                if fs.exists(save_path):
                    self.print("Path %s already exists. Skipping..." % save_path)
                    continue
                self.print("Creating %s:%s" % (test_storage, save_path))
                fs.makedirs(unicode(save_path))
                # Write config
                config = cfg[beef.uuid][0] if beef.uuid in cfg else cfg[""][0]
                config["beef"] = str(beef.uuid)
                self.print("Writing %s:%s/test-config.yml" % (test_storage, save_path))
                fs.setbytes(unicode(os.path.join(save_path, "test-config.yml")),
                            yaml.dump(config, default_flow_style=False))
                # Write beef
                self.print("Writing %s:%s/beef.json.bz2" % (test_storage, save_path))
                beef.save(test_storage, unicode(os.path.join(save_path, "beef.json.bz2")))
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
                data = fs.getbytes(unicode(os.path.join(test_path, "test-config.yml")))
                cfg = yaml.load(data)
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
            script = "%s.%s" % (beef.box.profile, test["script"])
            scls = loader.get_script(script)
            if not scls:
                self.die("Failed to load script '%s'" % script)
            # Build credentials
            credentials = {
                "address": beef.uuid,
                "cli_protocol": "beef",
                "beef_storage_url": test_st.url,
                "beef_path": beef_path,
                "access_preference": test.get("access_preference", "SC")
            }
            # Build version
            version = {
                "vendor": beef.box.vendor,
                "platform": beef.box.platform,
                "version": beef.box.version
            }
            # @todo: Input
            scr = scls(
                service=service,
                credentials=credentials,
                capabilities=caps,
                version=version,
                timeout=3600,
                name=script
            )
            self.print("[%04d] Running %s" % (n, test["script"]))
            result = scr.run()
            tc = {
                "script": script,
                "capabilities": caps,
                "credentials": credentials,
                "version": version,
                "input": {},
                "result": result
            }
            data = bz2.compress(ujson.dumps(tc))
            #
            rn = os.path.join(test_path, "%04d.%s.json.bz2" % (n, test["script"]))
            self.print("[%04d] Writing %s" % (n, rn))
            with test_st.open_fs() as fs:
                fs.setbytes(unicode(rn), data)

    def get_storage(self, name, beef=False, beef_test=False, beef_test_config=False):
        """
        Get beef storage by name
        :param name:
        :param beef:
        :param beef_test:
        :param beef_test_config:
        :return:
        """
        st = ExtStorage.get_by_name(name)
        if not st:
            self.die("Invalid storage '%s'" % name)
        if beef and st.type != "beef":
            self.die("Storage is not configured for beef")
        if beef_test and st.type != "beef_test":
            self.die("Storage is not configured for beef_test")
        if beef_test_config and st.type != "beef_test_config":
            self.die("Storage is not configured for beef_test_config")
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
            self.die("Failed to load beef: %s" % e)

    def get_config(self, storage=None, path=None):
        r = defaultdict(list)
        if path:
            path += "*"
        for config_st in self.iter_storage(name=storage, beef_test_config=True):
            with config_st.open_fs() as fs:
                for config_path in fs.walk.files(filter=path):
                    cfg = fs.getbytes(unicode(config_path))
                    data = yaml.load(cfg)
                    r[data.get("beef", "")] += [data]
        return r

    @staticmethod
    def iter_storage(name, beef=False, beef_test=False, beef_test_config=False):
        """
        Get beef storage by name
        :param name:
        :param beef:
        :param beef_test:
        :param beef_test_config:
        :return:
        """
        st = ExtStorage.objects.filter()
        if name:
            st = st.filter(name=name)
        else:
            if beef:
                st = st.filter(type="beef")
            elif beef_test:
                st = st.filter(type="beef_test")
            elif beef_test_config:
                st = st.filter(type="beef_test_config")
        for s in st:
            yield s

    def get_beefs(self, storage=None, path=None, uuids=None):
        """
        Get beef storage by name
        :param storage:
        :param path:
        :param uuids:
        :return:
        """
        r = {}
        if path:
            path += "*"
        for storage in self.iter_storage(name=storage, beef=True):
            # self.print("\n%sStorage: %s%s\n" % ("=" * 20, storage.name, "=" * 20))
            st_fs = storage.open_fs()
            for beef_path in st_fs.walk.files(filter=path):
                beef = self.get_beef(storage, beef_path)
                if uuids and beef.uuid not in uuids:
                    continue
                r[(st_fs, beef_path)] = beef
        return r

    rx_arg = re.compile(
        r"^(?P<name>[a-zA-Z][a-zA-Z0-9_]*)(?P<op>:?=@?)(?P<value>.*)$"
    )

    def get_script_args(self, arguments):
        """
        Parse arguments and return script's
        """
        def read_file(path):
            if not os.path.exists(path):
                self.die("Cannot open file '%s'" % path)
            with open(path) as f:
                return f.read()

        def parse_json(j):
            try:
                return ujson.loads(j)
            except ValueError as e:
                self.die("Failed to parse JSON: %s" % e)

        args = {}
        for a in arguments:
            match = self.rx_arg.match(a)
            if not match:
                self.die("Malformed parameter: '%s'" % a)
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
