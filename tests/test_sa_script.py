# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test sa scripts
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import glob
import unittest2
import os
## Third-party modules
from nose2.tools import params
from noc.core.script.loader import loader
from noc.core.script.beef import Beef


def iter_sa_beef():
    """
    Enumarate all available beef
    """
    for path in glob.glob(
        os.path.join(Beef.BEEF_ROOT, "*/*/*/*/*.json")
    ):
        yield path


class ServiceStub(object):
    class ServiceConfig(object):
        def __init__(self, pool, tos=None):
            self.pool = pool
            self.tos = tos

    def __init__(self, pool="default"):
        self.config = self.ServiceConfig(pool=pool)


class Test(unittest2.TestCase):
    @params(*tuple(iter_sa_beef()))
    def test_sa_script(self, path):
        """ Test SA script """
        beef = Beef()
        beef.load(path)
        script_class = loader.get_script(beef.script)
        assert script_class, "Cannot load script %s" % beef.script
        service = ServiceStub()
        # Emulate credentials
        credentials = {
            "address": beef.guid,
            "cli_protocol": "beef",
            "beef": beef
        }
        # Emulate capabilities
        caps = {}
        if beef.snmp_get or beef.snmp_getnext:
            caps["SNMP"] = True
            credentials["snmp_ro"] = "public"
        # Create script
        script = script_class(
            service=service,
            credentials=credentials,
            capabilities=caps,
            version={
                "vendor": beef.vendor,
                "platform": beef.platform,
                "version": beef.version
            },
            timeout=30,
            name=beef.script
        )
        result = script.run()
        # Cleanup result
        if beef.ignore_timestamp_mismatch:
            beef_result = beef.clean_timestamp(beef.result)
            result = beef.clean_timestamp(result)
        else:
            beef_result = beef.result
        # Compare results
        self.assertEqual(beef_result, result)
