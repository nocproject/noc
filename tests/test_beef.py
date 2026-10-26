# ----------------------------------------------------------------------
# Beef test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import bz2
import re

# Third-party modules
import orjson
import pytest
from gufo.blob.sync import open_blob

# NOC modules
from noc.config import config
from noc.core.ioloop.util import setup_asyncio
from noc.core.script.loader import loader

rx_tc = re.compile(r"^.+/\d\d\d\d\.\S+\.json\.bz2")


class ServiceStub:
    class ServiceConfig:
        def __init__(self, pool, tos=None) -> None:
            self.pool = pool
            self.tos = tos

    def __init__(self, pool) -> None:
        self.config = self.ServiceConfig(pool=pool)
        setup_asyncio()


def get_beef_tests() -> list[tuple[str, str]]:
    r: list[tuple[str, str]] = []
    paths = config.tests.beef_paths or []
    for url in paths:
        with open_blob(url) as blob:
            for key in blob.scan(""):
                if rx_tc.match(key):
                    r.append((url, key))
    return r


@pytest.mark.parametrize(("url", "path"), get_beef_tests())
def test_beef(url: str, path: str) -> None:
    with open_blob(url) as blob:
        test = orjson.loads(bz2.decompress(blob[path]))
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
