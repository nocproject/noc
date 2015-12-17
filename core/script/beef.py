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
import uuid
import os
import glob
import datetime
## NOC modules
from noc.lib.fileutils import safe_rewrite


class Beef(object):
    beef_args = [
        "script", "vendor", "platform", "version", "input",
        "result", "cli", "snmp_get", "snmp_getnext", "http_get", "motd",
        "mock_get_version", "ignore_timestamp_mismatch", "maxDiff",
        "date", "private", "guid", "type"]

    type_signature = "script::beef"
    BEEF_ROOT = "var/beef/sa"

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
                return dict((str(k), q(s[k])) for k in s)
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
        return self

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

    @classmethod
    def load_by_id(cls, beef_id):
        """
        Find beef by ID or by path
        :return: Beef instance or None
        """
        # Load from file
        if os.path.isfile(beef_id):
            beef = Beef()
            beef.load(beef_id)
            return beef
        # Load by UUID
        try:
            uuid.UUID(beef_id)
        except ValueError:
            return None
        #
        for path in glob.glob(os.path.join(
            cls.BEEF_ROOT, "*/*/*/*/%s.json" % beef_id
        )):
            beef = Beef()
            beef.load(path)
            return beef
        return None

    def save(self, path):
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
        if not beef.get("date"):
            beef["date"] = datetime.datetime.now()
        if not beef.get("guid"):
            beef["guid"] = str(uuid.uuid4())
        beef = q(beef)
        safe_rewrite(path, json.dumps(beef), mode=0644)
