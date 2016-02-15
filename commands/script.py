# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc script
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import argparse
import pprint
import re
import json
## NOC modules
from noc.core.management.base import BaseCommand
from noc.lib.validators import is_int
from noc.core.script.loader import loader


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--config",
            action="store",
            dest="config",
            default=os.environ.get("NOC_CONFIG", "etc/noc.yml"),
            help="Configuration path"
        )
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

    def handle(self, config, script, object_name, arguments, pretty,
               yaml, use_snmp,
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
            script = "%s.%s" % (obj.profile_name, script)
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
        # Run script
        service = ServiceStub(pool=obj.pool.name)
        scr = script_class(
            service=service,
            credentials=credentials,
            capabilities=caps,
            args=args,
            version=None,  #@todo: Fix
            timeout=3600,
            name=script
        )
        result = scr.run()
        if pretty:
            pprint.pprint(result)
        elif yaml:
            import yaml
            import sys
            yaml.dump(result, sys.stdout)
        else:
            print result

    def get_object(self, object_name):
        """
        Resolve object by name or by id
        """
        from noc.sa.models.managedobject import ManagedObject
        from django.db.models import Q

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
            "path": obj.remote_path
        }
        if creds.snmp_ro:
            credentials["snmp_version"] = "v2c"
            credentials["snmp_ro"] = creds.snmp_ro
        if obj.scheme in (1, 2):
            credentials["cli_protocol"] = {
                1: "telnet",
                2: "ssh"
            }[obj.scheme]
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
                return json.loads(j)
            except ValueError, why:
                self.die("Failed to parse JSON: %s" % why)

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
