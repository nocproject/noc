# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ./noc script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import argparse
import pprint
import re
# Third-party modules
import ujson
# NOC modules
from noc.core.management.base import BaseCommand
from noc.lib.validators import is_int
from noc.core.script.loader import loader


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Output options
        out_group = parser.add_mutually_exclusive_group()
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
        parser.add_argument(
            "--without-snmp",
            action="store_false",
            dest="use_snmp",
            help="Disable SNMP"
        )
        parser.add_argument(
            "--beef",
            help="Collect beef to file"
        )
        parser.add_argument(
            "script",
            nargs=1,
            help="Script name"
        )
        parser.add_argument(
            "object_name",
            nargs=1,
            help="Object name"
        )
        parser.add_argument(
            "arguments",
            nargs=argparse.REMAINDER,
            help="Arguments passed to script"
        )

    def handle(self, script, object_name, arguments, pretty,
               yaml, use_snmp, beef,
               *args, **options):
        # Get object
        obj = self.get_object(object_name[0])
        # Build credentials
        credentials = self.get_credentials(obj)
        # Parse arguments
        args = self.get_script_args(arguments)
        # Load script
        script = script[0]
        if "." not in script:
            script = "%s.%s" % (obj.profile.name, script)
        script_class = loader.get_script(script)
        if not script_class:
            self.die("Failed to load script %s" % script_class)
        # Get capabilities
        caps = obj.get_caps()
        #
        if not use_snmp:
            if "snmp_ro" in credentials:
                del credentials["snmp_ro"]
            if "SNMP" in caps:
                del caps["SNMP"]
        # Get version info
        v = obj.version
        p = obj.platform
        if v:
            version = {
                "vendor": v.vendor.name,
                "platform": p.name,
                "version": v.version if v else None
            }
        else:
            version = None
        # Run script
        service = ServiceStub(pool=obj.pool.name)
        scr = script_class(
            service=service,
            credentials=credentials,
            capabilities=caps,
            args=args,
            version=version,
            timeout=3600,
            name=script,
            collect_beef=bool(beef)
        )
        result = scr.run()
        if pretty:
            pprint.pprint(result)
        elif yaml:
            import yaml
            import sys
            yaml.dump(result, sys.stdout)
        else:
            self.stdout.write("%s\n" % result)
        if beef:
            if scr.version:
                scr.beef.set_version(**scr.version)
            else:
                # @todo: Fix
                self.stdout.write("Warning! Beef contains no version info\n")
            scr.beef.set_result(result)
            if scr._motd:
                scr.beef.set_motd(scr._motd)
            if os.path.isdir(beef):
                beef = os.path.join(beef, "%s.json" % scr.beef.uuid)
            self.stdout.write("Writing beef to %s\n" % beef)
            scr.beef.save(beef)

    def get_object(self, object_name):
        """
        Resolve object by name or by id
        """
        from noc.sa.models.managedobject import ManagedObject
        from django.db.models import Q

        if object_name.endswith(".json") and os.path.isfile(object_name):
            return JSONObject(object_name)
        q = Q(name=object_name)
        if is_int(object_name):
            q = Q(id=int(object_name)) | q
        try:
            return ManagedObject.objects.get(q)
        except ManagedObject.DoesNotExist:
            self.die("Object is not found: %s" % object_name)

    def get_credentials(self, obj):
        """
        Returns object's credentials
        """
        creds = obj.credentials

        credentials = {
            "address": obj.address,
            "user": creds.user,
            "password": creds.password,
            "super_password": creds.super_password,
            "path": obj.remote_path,
            "raise_privileges": obj.to_raise_privileges
        }
        if creds.snmp_ro:
            credentials["snmp_version"] = "v2c"
            credentials["snmp_ro"] = creds.snmp_ro
        if obj.scheme in (1, 2):
            credentials["cli_protocol"] = {
                1: "telnet",
                2: "ssh"
            }[obj.scheme]
            if obj.port:
                credentials["cli_port"] = obj.port
        elif obj.scheme in (3, 4):
            credentials["http_protocol"] = "https" if obj.scheme == 4 else "http"
            if obj.port:
                credentials["http_port"] = obj.port
        return credentials

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


class PoolStub(object):
    def __init__(self, name):
        self.name = name


class ProfileStub(object):
    def __init__(self, name):
        self.name = name


class VendorStub(object):
    def __init__(self, name):
        self.name = name


class PlatformStub(object):
    def __init__(self, name):
        self.name = name


class VersionStub(object):
    def __init__(self, version):
        self.version = version


class JSONObject(object):
    def __init__(self, path):
        with open(path) as f:
            data = ujson.load(f)
        self.scheme = {
            "telnet": 1,
            "ssh": 2
        }.get(data.get("scheme", "telnet"), 1)
        self.profile = ProfileStub(data.get("profile"))
        self.address = data["address"]
        self.port = data.get("port")
        self.creds = data.get("credentials", {})
        self.caps = data.get("caps")
        self.remote_path = None
        self.to_raise_privileges = data.get("raise_privileges", True)
        self.pool = PoolStub("default")
        self.vendor = VendorStub(data["vendor"]) if "vendor" in data else None
        self.platform = PlatformStub(data["platform"]) if "platform" in data else None
        self.version = VersionStub(data["version"]) if "version" in data else None

    @property
    def credentials(self):
        from noc.sa.models.managedobject import Credentials
        return Credentials(**dict(
            (k, self.creds.get(k))
            for k in ("user", "password", "super_password", "snmp_ro", "snmp_rw")
        ))

    def get_caps(self):
        return self.caps


if __name__ == "__main__":
    Command().run()
