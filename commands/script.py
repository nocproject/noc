# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ./noc script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import os
import argparse
import pprint
import re
# Third-party modules
import ujson
# NOC modules
from noc.core.management.base import BaseCommand
from noc.lib.validators import is_int
from noc.core.span import get_spans, Span
from noc.core.script.loader import loader
from noc.core.script.scheme import CLI_PROTOCOLS, HTTP_PROTOCOLS, PROTOCOLS, BEEF, TELNET, SSH


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
            "--access-preference",
            dest="access_preference",
            help="Alter access method preference"
        )
        parser.add_argument(
            "--update-spec",
            help="Append all issued commands to spec"
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
               yaml, use_snmp, access_preference, update_spec,
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
        if access_preference:
            credentials["access_preference"] = access_preference
        # Get version info
        if obj.version:
            version = {
                "vendor": obj.vendor.name if obj.vendor else None,
                "platform": obj.platform.name if obj.platform else None,
                "version": obj.version.version if obj.version else None
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
            name=script
        )
        span_sample = 1 if update_spec else 0
        with Span(sample=span_sample):
            result = scr.run()
        if pretty:
            pprint.pprint(result)
        elif yaml:
            import yaml
            import sys
            yaml.dump(result, sys.stdout)
        else:
            self.stdout.write("%s\n" % result)
        if update_spec:
            self.update_spec(update_spec, scr)

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
            "raise_privileges": obj.to_raise_privileges,
            "access_preference": obj.get_access_preference()
        }
        if creds.snmp_ro:
            credentials["snmp_version"] = "v2c"
            credentials["snmp_ro"] = creds.snmp_ro
        if obj.scheme in CLI_PROTOCOLS:
            credentials["cli_protocol"] = PROTOCOLS[obj.scheme]
            if obj.port:
                credentials["cli_port"] = obj.port
        elif obj.scheme in HTTP_PROTOCOLS:
            credentials["http_protocol"] = PROTOCOLS[obj.scheme]
            if obj.port:
                credentials["http_port"] = obj.port
        if (
            obj.scheme == BEEF and
            obj.object_profile.beef_storage and
            obj.object_profile.beef_path_template
        ):
            beef_path = obj.object_profile.beef_path_template.render_subject(object=obj)
            if beef_path:
                credentials["beef_storage_url"] = obj.object_profile.beef_storage.url
                credentials["beef_path"] = beef_path
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

    def update_spec(self, name, script):
        """
        Update named spec
        :param name: Spec name
        :param script: BaseScript instance
        :return:
        """
        from noc.dev.models.quiz import Quiz
        from noc.dev.models.spec import Spec, SpecAnswer
        from noc.sa.models.profile import Profile

        self.print("Updating spec: %s" % name)
        spec = Spec.get_by_name(name)
        changed = False
        if not spec:
            self.print("   Spec not found. Creating")
            # Get Ad-Hoc quiz
            quiz = Quiz.get_by_name("Ad-Hoc")
            if not quiz:
                self.print("   'Ad-Hoc' quiz not found. Skipping")
                return
            # Create Ad-Hoc spec for profile
            spec = Spec(
                name,
                description="Auto-generated Ad-Hoc spec for %s profile" % script.profile.name,
                revision=1,
                quiz=quiz,
                author="NOC",
                profile=Profile.get_by_name(script.profile.name),
                changes=[],
                answers=[]
            )
            changed = True
        # Fetch commands from spans
        cli_svc = {"beef_cli", "cli", "telnet", "ssh"}
        commands = set()
        for sd in get_spans():
            row = sd.split("\t")
            if row[6] not in cli_svc:
                continue
            commands.add(row[12].decode("string_escape").strip())
        # Update specs
        s_name = "cli_%s" % script.name.rsplit(".", 1)[-1]
        names = set()
        for ans in spec.answers:
            if (
                (ans.name == s_name or ans.name.startswith(s_name + ".")) and
                    ans.type == "cli"
            ):
                names.add(ans.name)
                if ans.value in commands:
                    # Already recorded
                    commands.remove(ans.value)
        if commands:
            # New commands left
            max_n = 0
            for n in names:
                if "." in n:
                    nn = int(n.rsplit(".", 1)[-1])
                    if nn > max_n:
                        max_n = nn
            #
            ntpl = "%s.%%d" % s_name
            for nn, cmd in enumerate(sorted(commands)):
                spec.answers += [SpecAnswer(
                    name=ntpl % (nn + 1),
                    type="cli",
                    value=cmd
                )]
            changed = True
        if changed:
            spec.save()


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
            "telnet": TELNET,
            "ssh": SSH
        }.get(data.get("scheme", "telnet"), TELNET)
        self.profile = ProfileStub(data.get("profile"))
        self.address = data["address"]
        self.port = data.get("port")
        self.creds = data.get("credentials", {})
        self.caps = data.get("caps")
        self.remote_path = None
        self.to_raise_privileges = data.get("raise_privileges", True)
        self.access_preference = data.get("access_preference", "CS")
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

    def get_access_preference(self):
        return self.access_preference


if __name__ == "__main__":
    Command().run()
