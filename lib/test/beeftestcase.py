# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Canned beef test case
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import cPickle
import re
import types
import datetime
import os
import uuid
## Django modules
from django.utils import unittest  # unittest2 backport
## NOC lib modules
from noc.sa.models import script_registry, profile_registry
from noc.lib.test.activatorstub import ActivatorStub
from noc.sa.protocols.sae_pb2 import AccessProfile
from noc.lib.fileutils import safe_rewrite, read_file
from noc.lib.serialize import json_encode, json_decode
import noc.settings


class BeefTestCase(unittest.TestCase):
    """
    Canned beef base class
    """
    beef_args = [
        "script", "vendor", "platform", "version", "input",
        "result", "cli", "snmp_get", "snmp_getnext", "http_get", "motd",
        "mock_get_version", "ignore_timestamp_mismatch", "maxDiff",
        "date", "private", "guid", "type"]

    type_signature = "script::beef"

    def __init__(self, *args, **kwargs):
        super(BeefTestCase, self).__init__(*args, **kwargs)
        self.guid = None
        self.maxDiff = None
        self.script = None
        self.vendor = None
        self.platform = None
        self.version = None
        self.input = {}
        self.result = None
        self.motd = ""
        self.cli = None
        self.snmp_get = {}
        self.snmp_getnext = {}
        self.http_get = {}
        self.mock_get_version = False  # Emulate get_version call
        self.ignore_timestamp_mismatch = False
        self.private = False
        self.type = self.type_signature

    def load_beef(self, path):
        """
        Load beef from JSON file
        :param path:
        :return:
        """
        def q(s):
            ts = type(s)
            if ts == dict:
                return dict((k, q(s[k])) for k in s)
            elif ts == list:
                return [q(x) for x in s]
            elif isinstance(s, basestring):
                return s.decode("string_escape")
            else:
                return s

        data = read_file(path)
        if not data:
            raise OSError("Cannot read file: %s" % path)
        beef = json_decode(data)
        if beef.get("type") != self.type_signature:
            raise ValueError("Invalid beef '%s'. Signature mismatch" % path)
        for n in self.beef_args:
            if n in beef:
                setattr(self, n, q(beef[n]))
        self._testMethodDoc = "%s [%s]" % (beef["script"], beef["guid"])

    def save_beef(self, path, **kwargs):
        def q(s):
            ts = type(s)
            if ts == datetime.datetime:
                return s.isoformat()
            elif ts == dict:
                return dict((k, q(s[k])) for k in s)
            elif ts == list:
                return [q(x) for x in s]
            elif ts == tuple:
                return tuple([q(x) for x in s])
            elif isinstance(s, basestring):
                return str(s).encode("string_escape")
            else:
                return s

        beef = dict((k, getattr(self, k, None)) for k in self.beef_args)
        beef.update(kwargs)
        if not beef.get("date"):
            beef["date"] = datetime.datetime.now()
        if not beef.get("guid"):
            beef["guid"] = str(uuid.uuid4())
        beef = q(beef)
        if os.path.isdir(path):
            path = os.path.join(path, beef["guid"] + ".json")
        safe_rewrite(path, json_encode(beef), mode=0644)
        return path

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

    def fix_beef(self, new_result):
        """
        Save fixed beef
        :param new_result:
        :return:
        """
        path = os.path.join(
            noc.settings.TEST_FIXED_BEEF_BASE, self.guid + ".json")
        self.save_beef(path, result=new_result)

    def runTest(self):
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
                                              "test", a, **self.input)
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
            if noc.settings.TEST_FIXED_BEEF_BASE and old_result != new_result:
                self.fix_beef(new_result)
            self.assertEquals(new_result, old_result)
        else:
            # Exception raised
            self.assertTrue(script.error_traceback is None,
                "Unhandled exception while running script:\n%s" % script.error_traceback)
