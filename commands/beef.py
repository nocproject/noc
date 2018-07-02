# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Beef management
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import argparse
# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.script.beef import Beef
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.dev.models.spec import Spec
from noc.main.models.extstorage import ExtStorage


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # collect command
        collect_parser = subparsers.add_parser("collect")
        collect_parser.add_argument(
            "--spec",
            help="Spec path or URL"
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
        # list command
        list_parser = subparsers.add_parser("list")  # noqa
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
        # fix command
        fix_parser = subparsers.add_parser("fix")
        fix_parser.add_argument(
            "beef",
            nargs=1,
            help="Beef UUID or path"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_collect(self, spec, objects, *args, **options):
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
            if mo.object_profile.beef_policy == "D":
                self.print("  Collection disabled by policy. Skipping")
                continue
            if not mo.object_profile.beef_storage:
                self.print("  Beef storage is not configured. Skipping")
                continue
            if not mo.object_profile.beef_path_template:
                self.print("  Beef path template is not configured. Skipping")
                continue
            storage = mo.object_profile.beef_storage
            path = mo.object_profile.beef_path_template.render_subject(
                object=mo,
                spec=sp
            )
            if not path:
                self.print("  Beef path is empty. Skipping")
                continue
            bdata = mo.scripts.get_beef(spec=req)
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
        st = self.get_beef_storage(storage)
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

    def handle_list(self, *args, **options):
        storage = options.get("storage")
        if not storage:
            storage = ExtStorage.objects.filter(enable_beef=True).first()
        r = ["UUID,Vendor,Platform,Version,SpecUUID,Changed,Path"]
        st_fs = storage.open_fs()
        for step in st_fs.walk(''):
            if not step.files:
                continue
            for file in step.files:
                beef = Beef.load(storage, file.make_path(step.path))
                r += [",".join([
                    beef.uuid,
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

    def handle_run(self, path, storage, script, pretty=False, yaml=False, *args, **options):
        from noc.core.script.loader import loader
        st = self.get_beef_storage(storage)
        beef = self.get_beef(st, path)
        # Build credentials
        credentials = {
            "address": beef.uuid,
            "cli_protocol": "beef",
            "beef_storage_url": st.url,
            "beef_path": path
        }
        # Get capabilities
        caps = {}
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
                name=s_name
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

    def handle_fix(self, beef, *args, **options):
        raise NotImplementedError()

    def get_beef_storage(self, name):
        """
        Get beef storage by nname
        :param name:
        :return:
        """
        st = ExtStorage.get_by_name(name)
        if not st:
            self.die("Invalid storage '%s'" % name)
        if not st.enable_beef:
            self.die("Storage is not configured for beef")
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


class ServiceStub(object):
    class ServiceConfig(object):
        def __init__(self, pool, tos=None):
            self.pool = pool
            self.tos = tos

    def __init__(self, pool):
        self.config = self.ServiceConfig(pool=pool)


if __name__ == "__main__":
    Command().run()
