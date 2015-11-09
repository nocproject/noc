# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Beef API
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import json
import re


class Beef(object):
    beef_args = [
        "script", "vendor", "platform", "version", "input",
        "result", "cli", "snmp_get", "snmp_getnext", "http_get", "motd",
        "mock_get_version", "ignore_timestamp_mismatch", "maxDiff",
        "date", "private", "guid", "type"]

    type_signature = "script::beef"

    def __init__(self):
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

    def load(self, path):
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

        with open(path) as f:
            beef = json.load(f)
        if beef.get("type") != self.type_signature:
            raise ValueError("Signature mismatch")
        for n in self.beef_args:
            if n in beef:
                setattr(self, n, q(beef[n]))

    rx_timestamp = re.compile(r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?$")

    @classmethod
    def clean_timestamp(cls, r):
        if isinstance(r, basestring):
            # Process strings
            if cls.rx_timestamp.match(r):
                # Fill timestamp by zeroes
                return "0000-00-00T00:00:00.000000"
            else:
                return r
        elif isinstance(r, (list, tuple)):
            # Iterate lists
            return [cls.clean_timestamp(x) for x in r]
        elif isinstance(r, dict):
            # Iterate hashes
            return dict([(k, cls.clean_timestamp(v)) for k, v in r.iteritems()])
        else:
            # Return unprocessed
            return r
