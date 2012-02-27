# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ScriptTestCase
##     Canned beef base class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import cPickle
import re
import types
import datetime
import os
## Django modules
from django.utils import unittest  # unittest2 backport
## NOC lib modules
from noc.sa.models import script_registry, profile_registry
from noc.lib.test.activatorstub import ActivatorStub
from noc.sa.protocols.sae_pb2 import AccessProfile
from noc.settings import TEST_FIXED_BEEF_BASE


class ScriptTestCase(unittest.TestCase):
    """
    Canned beef base class
    """
    maxDiff = None
    script = None
    vendor = None
    platform = None
    version = None
    input = {}
    result = None
    motd = ""
    cli = None
    snmp_get = {}
    snmp_getnext = {}
    http_get = {}
    mock_get_version = False  # Emulate get_version call
    ignore_timestamp_mismatch = False

    rx_timestamp = re.compile(r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?$")

    @classmethod
    def save_beef(cls, path, **kwargs):
        """
        Save canned beef to file
        :param cls:
        :param path:
        :param kwargs:
        :return:
        """
        def format_stringdict(d):
            def lrepr(s):
                return repr(s)[1:-1]

            out = ["{"]
            for k, v in d.items():
                lines = v.splitlines()
                if len(lines) < 4:
                    out += ["%s:  %s, " % (repr(k), repr(v))]
                else:
                    out += ["## %s" % repr(k)]
                    out += ["%s: \"\"\"%s" % (repr(k), lrepr(lines[0]))]
                    out += [lrepr(l) for l in lines[1:-1]]
                    out += ["%s\"\"\", " % lrepr(lines[-1])]
            out += ["}"]
            return "\n".join(out)

        import pprint
        from django.template import loader
        from noc.lib.fileutils import safe_rewrite

        script = kwargs.get("script", cls.script)

        beef = loader.render_to_string("sa/templates/beef.py.tpl", {
            "script": script,
            "test_name": script.replace(".", "_") + "_Test",
            "vendor": kwargs.get("vendor", cls.vendor),
            "platform": kwargs.get("platform", cls.platform),
            "version": kwargs.get("version", cls.version),
            "date": datetime.datetime.now(),
            "input": pprint.pformat(kwargs.get("input", cls.input)),
            "result": pprint.pformat(kwargs.get("result", cls.result)),
            "cli": format_stringdict(kwargs.get("cli", cls.cli)),
            "snmp_get": pprint.pformat(kwargs.get("snmp_get", cls.snmp_get)),
            "snmp_getnext": pprint.pformat(kwargs.get("snmp_getnext",
                                                     cls.snmp_getnext)),
            "http_get": pprint.pformat(kwargs.get("http_get", cls.http_get)),
            "motd": pprint.pformat(kwargs.get("motd", cls.motd))
        })
        safe_rewrite(path, beef)

    def clean_timestamp(self, r):
        if isinstance(r, basestring):
            # Process strings
            if self.rx_timestamp.match(r):
                # Fill timestamp by zeroes
                return "0000-00-00T00:00:00.000000"
            else:
                return r
        elif type(r) in (types.ListType, types.TupleType):
            # Iterate lists
            return [self.clean_timestamp(x) for x in r]
        elif type(r) == types.DictType:
            # Iterate hashes
            return dict([(k, self.clean_timestamp(v)) for k, v in r.items()])
        else:
            # Return unprocessed
            return r

    def fix_beef(self, new_result):
        """
        Save fixed beef
        :param new_result:
        :return:
        """
        l = [TEST_FIXED_BEEF_BASE] + self.__class__.__module__.split(".")[1:]
        path = os.path.join(*l) + ".py"
        self.save_beef(path, result=new_result)

    def test_script(self):
        p = self.script.split(".")
        profile = profile_registry[".".join(p[:2])]()
        # Prepare access profile
        a = AccessProfile()
        a.profile = profile.name
        if self.snmp_get or self.snmp_getnext:
            a.snmp_ro = "public"
        if self.http_get:
            a.scheme = 2
        # Run script.
        script = script_registry[self.script](profile, ActivatorStub(self),
                                              a, **self.input)
        # Install mock get_version into cache, if necessary
        s = self.script.split(".")
        if self.mock_get_version and s[-1] != "get_version":
            # Install version info into script call cache
            version = {
                "vendor": self.vendor,
                "platform": self.platform,
                "version": self.version
            }
            script.set_cache("%s.%s.get_version" % (s[0], s[1]), {}, version)
        script.run()
        # Parse script result
        if script.result:
            # Script completed successfully
            result = cPickle.loads(script.result)
            if self.ignore_timestamp_mismatch:
                new_result = self.clean_timestamp(result)
                old_result = self.clean_timestamp(self.result)
            else:
                new_result = result
                old_result = self.result
            if TEST_FIXED_BEEF_BASE and old_result != new_result:
                self.fix_beef(new_result)
            self.assertEquals(new_result, old_result)
        else:
            # Exception raised
            self.assertEquals(script.error_traceback, None)
