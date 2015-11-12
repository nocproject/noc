# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc script
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import argparse
import pprint
import logging
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
        parser.add_argument(
            "--pretty",
            action="store_true",
            dest="pretty",
            default=False,
            help="Pretty-print output"
        )
        parser.add_argument(
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
        ),
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


class ServiceStub(object):
    class ServiceConfig(object):
        def __init__(self, pool, tos=None):
            self.pool = pool
            self.tos = tos

    def __init__(self, pool):
        self.config = self.ServiceConfig(pool=pool)


if __name__ == "__main__":
    Command().run()
