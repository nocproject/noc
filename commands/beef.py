# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Beef management
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import pprint
import glob
import os
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
        test_parser = subparsers.add_parser("test")
        test_parser.add_argument(
            "beef",
            nargs=1,
            help="Beef UUID or path"
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
        st = ExtStorage.get_by_name(storage)
        if not st:
            self.die("Invalid storage '%s'" % storage)
        if not st.enable_beef:
            self.die("Storage is not configured for beef")
        try:
            beef = Beef.load(st, path)
        except IOError as e:
            self.die("Failed to load beef: %s" % e)
        r = [
            "UUID     : %s" % beef.uuid,
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
            r += ["-------- Request: %s" % c.request]
            for n, reply in enumerate(c.reply):
                r += [
                    "-------- Packet #%d" % n,
                    "%r" % beef._cli_decoder(reply)
                ]
        # Dump output
        self.stdout.write("\n".join(r) + "\n")
        return

    def handle_list(self, *options, **args):
        r = ["Provider,Profile,Script,Vendor,Platform,Version,UUID"]
        for path in glob.glob(
            os.path.join(Beef.BEEF_ROOT, "*/*/*/*/*.json")
        ):
            parts = path.split(os.sep)
            provider = parts[3]
            b = Beef()
            b.load(path)
            profile, script = b.script.rsplit(".", 1)
            r += ["%s,%s,%s,%s,%s,%s,%s" % (
                provider, profile, script,
                b.vendor, b.platform, b.version, b.uuid)]
        # Dump output
        self.stdout.write("\n".join(r) + "\n")
        return

    def handle_test(self, beef, *options, **args):
        self.run_beef(beef)

    def handle_fix(self, beef, *options, **args):
        self.run_beef(beef, fix=True)

    def run_beef(self, beef, fix=False):
        from noc.core.script.loader import loader

        b = Beef.load_by_id(beef[0])
        if not b:
            self.die("Beef not found: %s" % beef[0])
        script_class = loader.get_script(b.script)
        if not script_class:
            self.die("Invalid script: %s" % b.script)
        # Build credentials
        credentials = {
            "address": b.uuid,
            "cli_protocol": "beef",
            "beef": b
        }
        # Get capabilities
        caps = {}
        # Run script
        service = ServiceStub(pool="default")
        scr = script_class(
            service=service,
            credentials=credentials,
            capabilities=caps,
            version={
                "vendor": b.vendor,
                "platform": b.platform,
                "version": b.version
            },
            timeout=3600,
            name=b.script
        )
        result = scr.run()
        pprint.pprint(result, stream=self.stdout)
        if fix and b.result != result:
            self.stdout.write("Fixing %s\n" % beef[0])
            b.result = result
            b.save(beef[0])


class ServiceStub(object):
    class ServiceConfig(object):
        def __init__(self, pool, tos=None):
            self.pool = pool
            self.tos = tos

    def __init__(self, pool):
        self.config = self.ServiceConfig(pool=pool)


if __name__ == "__main__":
    Command().run()
