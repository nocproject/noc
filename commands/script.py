# ----------------------------------------------------------------------
# ./noc script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import argparse
import pprint
import datetime
import re
from collections import namedtuple

# Third-party modules
from fs import open_fs
import orjson
import yaml
import codecs
import uuid

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.validators import is_int
from noc.core.span import get_spans, Span
from noc.core.script.loader import loader
from noc.core.script.beef import Beef
from noc.core.script.scheme import (
    CLI_PROTOCOLS,
    HTTP_PROTOCOLS,
    PROTOCOLS,
    BEEF,
    TELNET,
    SSH,
    HTTP,
    HTTPS,
)
from noc.core.mongo.connection import connect
from noc.core.comp import smart_text, smart_bytes

BEEF_FORMAT = "1"
CLI_ENCODING = "quopri"
MIB_ENCODING = "base64"
Credentials = namedtuple(
    "Credentials", ["user", "password", "super_password", "snmp_ro", "snmp_rw", "snmp_rate_limit"]
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Output options
        out_group = parser.add_mutually_exclusive_group()
        out_group.add_argument(
            "--pretty",
            action="store_true",
            dest="pretty",
            default=False,
            help="Pretty-print output",
        )
        out_group.add_argument(
            "--yaml", action="store_true", dest="yaml_o", default=False, help="YAML output"
        )
        parser.add_argument(
            "--without-snmp", action="store_false", dest="use_snmp", help="Disable SNMP"
        )
        parser.add_argument(
            "--access-preference", dest="access_preference", help="Alter access method preference"
        )
        parser.add_argument(
            "--snmp-rate-limit",
            type=int,
            default=0,
            dest="snmp_rate_limit",
            help="Set SNMP Rate-limit setting",
        )
        parser.add_argument("--update-spec", help="Append all issued commands to spec")
        parser.add_argument(
            "-o", dest="beef_output", type=smart_text, help="Save script output to beef"
        )
        parser.add_argument("script", nargs=1, help="Script name")
        parser.add_argument("object_name", nargs=1, help="Object name")
        parser.add_argument(
            "arguments", nargs=argparse.REMAINDER, help="Arguments passed to script"
        )

    def handle(
        self,
        script,
        object_name,
        arguments,
        pretty,
        yaml_o,
        use_snmp,
        access_preference,
        snmp_rate_limit,
        update_spec,
        beef_output,
        *args,
        **options,
    ):
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
        if snmp_rate_limit:
            credentials["snmp_rate_limit"] = snmp_rate_limit
        # Get version info
        if obj.version:
            version = {
                "vendor": obj.vendor.name if obj.vendor else None,
                "platform": obj.platform.name if obj.platform else None,
                "version": obj.version.version if obj.version else None,
            }
            if obj.software_image:
                version["image"] = obj.software_image if obj.software_image else None
            # if getattr(obj, "get_caps", None):
            #    attrs = {x["key"]: x["value"] for x in obj.managedobjectattribute_set.values()}
            #    if attrs:
            #        version["attributes"] = attrs
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
        )
        span_sample = 1 if update_spec or beef_output else 0
        result = ""
        if beef_output:
            scr.start_tracking()
        with Span(sample=span_sample, suppress_trace=span_sample):
            result = scr.run()
        if pretty:
            pprint.pprint(result)
        elif yaml_o:
            import sys

            yaml.dump(result, sys.stdout)
        else:
            self.stdout.write("%s\n" % result)
        if update_spec:
            self.update_spec(update_spec, scr)
        if beef_output:
            bdata = self.get_beef(scr, obj)
            beef = Beef.from_json(bdata)
            storage = StorageStub("osfs:///")
            sdata = beef.get_data(decode=True)
            with storage.open_fs() as fs:
                fs.writebytes(beef_output, smart_bytes(yaml.safe_dump(sdata)))

    def get_object(self, object_name):
        """
        Resolve object by name or by id
        """
        if object_name.endswith(".json") and os.path.isfile(object_name):
            return JSONObject(object_name)

        from noc.sa.models.managedobject import ManagedObject
        from django.db.models import Q

        connect()

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
            "name": obj.name,
            "address": obj.address,
            "user": creds.user,
            "password": creds.password,
            "super_password": creds.super_password,
            "path": obj.remote_path,
            "raise_privileges": obj.to_raise_privileges,
            "access_preference": obj.get_access_preference(),
            "snmp_rate_limit": obj.snmp_rate_limit or None,
        }
        if (
            not creds.snmp_security_level or creds.snmp_security_level == "Community"
        ) and creds.snmp_ro:
            credentials["snmp_version"] = "v2c"
            credentials["snmp_ro"] = creds.snmp_ro
        elif creds.snmp_security_level in {"noAuthNoPriv", "authNoPriv", "authPriv"}:
            credentials["snmp_version"] = "v3"
            credentials["snmp_username"] = creds.snmp_username
            credentials["snmp_ctx_name"] = creds.snmp_ctx_name
            if creds.snmp_security_level in {"authNoPriv", "authPriv"}:
                credentials["snmp_auth_key"] = creds.snmp_auth_key
                credentials["snmp_auth_proto"] = creds.snmp_auth_proto
            if creds.snmp_security_level == "authPriv":
                credentials["snmp_priv_key"] = creds.snmp_priv_key
                credentials["snmp_priv_proto"] = creds.snmp_priv_proto
        if obj.scheme in CLI_PROTOCOLS:
            credentials["cli_protocol"] = PROTOCOLS[obj.scheme]
            if obj.port:
                credentials["cli_port"] = obj.port
        elif obj.scheme in HTTP_PROTOCOLS:
            credentials["http_protocol"] = PROTOCOLS[obj.scheme]
            if obj.port:
                credentials["http_port"] = obj.port
        if (
            obj.scheme == BEEF
            and obj.object_profile.beef_storage
            and obj.object_profile.beef_path_template
        ):
            beef_path = obj.object_profile.beef_path_template.render_subject(object=obj)
            if beef_path:
                credentials["beef_storage_url"] = obj.object_profile.beef_storage.url
                credentials["beef_path"] = beef_path
        return credentials

    rx_arg = re.compile(r"^(?P<name>[a-zA-Z][a-zA-Z0-9_]*)(?P<op>:?=@?)(?P<value>.*)$")

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
                return orjson.loads(j)
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

    def update_spec(self, name, script, save=True):
        """
        Update named spec
        :param name: Spec name
        :param script: BaseScript instance
        :param save:
        :return:
        """
        from noc.dev.models.quiz import Quiz
        from noc.dev.models.spec import Spec, SpecAnswer
        from noc.sa.models.profile import Profile

        connect()
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
                answers=[],
            )
            changed = True
        # Fetch commands from spans
        cli_svc = {"beef_cli", "cli", "telnet", "ssh"}
        commands = set()
        for span in get_spans():
            if span.service not in cli_svc:
                continue
            # Delete last \\n symbol and add command
            commands.add(span.in_label[:-1].decode("string_escape").strip())
        # Update specs
        s_name = "cli_%s" % script.name.rsplit(".", 1)[-1]
        names = set()
        for ans in spec.answers:
            if (ans.name == s_name or ans.name.startswith(s_name + ".")) and ans.type == "cli":
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
                spec.answers += [SpecAnswer(name=ntpl % (nn + 1), type="cli", value=cmd)]
            changed = True
        if not save:
            return spec
        if changed:
            spec.save()

    def get_beef(self, script, obj):
        result = {
            "version": BEEF_FORMAT,
            "uuid": str(uuid.uuid4()),
            "spec": None,
            "changed": datetime.datetime.now().isoformat(),
            "cli": [],
            "cli_fsm": [],
            "mib": [],
            "mib_encoding": MIB_ENCODING,
            "cli_encoding": CLI_ENCODING,
        }
        # Process CLI answers
        result["cli"] = self.get_cli_results(script)
        # Apply CLI fsm states
        result["cli_fsm"] = self.get_cli_fsm_results(script)
        # Apply MIB snapshot
        # self.logger.debug("Collecting MIB snapshot")
        # result["mib"] = self.get_snmp_results(spec)
        # Process version reply
        if script.version:
            result["box"] = script.version
        else:
            result["box"] = {
                "vendor": smart_text(obj.vendor.name) if obj.vendor else "Unknown",
                "platform": obj.platform.name if obj.platform else "Unknown",
                "version": obj.version.version if obj.version else "Unknown",
            }
        result["box"]["profile"] = obj.profile.name
        return result

    def get_cli_results(self, script):
        r = []
        cmd_num = 1
        for rcmd, packets in script.iter_cli_tracking():
            r += [
                {
                    "names": ["cli_%d" % cmd_num],
                    "request": rcmd,
                    "reply": [self.encode_cli(v) for v in packets],
                }
            ]
            cmd_num += 1
        script.stop_tracking()
        return r

    def get_cli_fsm_results(self, script):
        r = []
        for state, reply in script.iter_cli_fsm_tracking():
            r += [{"state": state, "reply": [self.encode_cli(v) for v in reply]}]
        return r

    @classmethod
    def encode_cli(cls, s):
        """
        Apply CLI encoding
        """
        return codecs.encode(smart_bytes(s), CLI_ENCODING)


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
            data = orjson.loads(f.read())
        self.scheme = {"telnet": TELNET, "ssh": SSH, "http": HTTP, "https": HTTPS}.get(
            data.get("scheme", "telnet"), TELNET
        )
        self.name = data.get("name", "")
        self.profile = ProfileStub(data.get("profile"))
        self.address = data["address"]
        self.port = data.get("port")
        self.creds = data.get("credentials", {})
        self.caps = data.get("caps")
        self.remote_path = self.creds.get("path")
        self.to_raise_privileges = data.get("raise_privileges", True)
        self.access_preference = data.get("access_preference", "CS")
        self.snmp_rate_limit = int(data.get("snmp_rate_limit", 0))
        self.pool = PoolStub("default")
        self.vendor = VendorStub(data["vendor"]) if "vendor" in data else None
        self.platform = PlatformStub(data["platform"]) if "platform" in data else None
        self.version = VersionStub(data["version"]) if "version" in data else None
        self.software_image = data["image"] if "image" in data else None
        self.managedobjectattribute_set = data["attributes"] if "attributes" in data else None

    @property
    def credentials(self):
        return Credentials(
            **{
                k: self.creds.get(k)
                for k in (
                    "user",
                    "password",
                    "super_password",
                    "snmp_ro",
                    "snmp_rw",
                    "snmp_rate_limit",
                    "snmp_security_level",
                    "snmp_username",
                    "snmp_ctx_name",
                    "snmp_auth_proto",
                    "snmp_auth_key",
                    "snmp_priv_proto",
                    "snmp_priv_key",
                )
            }
        )

    def get_caps(self):
        return self.caps

    def get_access_preference(self):
        return self.access_preference


class StorageStub(object):
    def __init__(self, url):
        self.url = url

    def open_fs(self):
        return open_fs(self.url)

    class Error(Exception):
        pass


if __name__ == "__main__":
    Command().run()
