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
## Django modules
from django.utils import unittest  # unittest2 backport
## NOC lib modules
from noc.lib.test.activatorstub import ActivatorStub
from noc.sa.profiles import profile_registry
from noc.sa.protocols.sae_pb2 import AccessProfile
from noc.sa.script import script_registry


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

    def test_script(self):
        p = self.script.split(".")
        profile = profile_registry[".".join(p[:2])]
        # Prepare access profile
        a = AccessProfile()
        a.profile = profile.name
        if self.snmp_get or self.snmp_getnext:
            a.snmp_ro = "public"
        if self.http_get:
            a.scheme = 2
        # Run script.
        script = script_registry[self.script](profile(), ActivatorStub(self),
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
                self.assertEquals(self.clean_timestamp(result),
                                  self.clean_timestamp(self.result))
            else:
                self.assertEquals(result, self.result)
        else:
            # Exception raised
            print script.error_traceback
            self.assertEquals(script.error_traceback, None)
