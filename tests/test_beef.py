# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Beef test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import bz2

# Third-party modules
import pytest
from fs import open_fs
import ujson

# NOC modules
from noc.config import config
from noc.core.script.loader import loader

rx_tc = re.compile(r"^.+/\d\d\d\d\.\S+\.json\.bz2")


class ServiceStub(object):
    class ServiceConfig(object):
        def __init__(self, pool, tos=None):
            self.pool = pool
            self.tos = tos

    def __init__(self, pool):
        self.config = self.ServiceConfig(pool=pool)


def get_beef_tests():
    r = []
    paths = config.tests.beef_paths or []
    for url in paths:
        fs = open_fs(url)
        for path in fs.walk.files(filter=["*.json.bz2"]):
            if rx_tc.match(path):
                r += [(fs, path)]
    return r


def beef_test_name(v):
    if isinstance(v, tuple):
        return v[1]
    return None


@pytest.fixture(params=get_beef_tests(), ids=beef_test_name)
def beef_test(request):
    return request.param


def test_beef(beef_test):
    fs, path = beef_test
    test = ujson.loads(bz2.decompress(fs.readbytes(path)))
    service = ServiceStub(pool="default")
    # Load script
    script = test["script"]
    scls = loader.get_script(script)
    assert scls
    # Build credentials
    # @todo: Input
    scr = scls(
        service=service,
        credentials=test["credentials"],
        capabilities=test["capabilities"],
        version=test["version"],
        timeout=3600,
        name=script,
    )
    result = scr.run()
    assert result == test["result"]
