# ----------------------------------------------------------------------
# Collector loader loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import inspect
# NOC modules
from .collectors.base import BaseCollector
from noc.config import config

BASE_PREFIX = os.path.join("services", "selfmon", "collectors")
PATHS = config.get_customized_paths(BASE_PREFIX)


def iter_collectors():
    global PATHS

    for path in PATHS:
        if not os.path.exists(path):
            continue
        b, _ = path.split(BASE_PREFIX)
        for f in sorted(os.listdir(path)):
            if not f.endswith(".py") or f.startswith("_") or f == "base.py":
                continue
            if b:
                base_name = os.path.basename(os.path.dirname(b))
            else:
                base_name = "noc"
            mn = "%s.%s.%s" % (base_name,
                               BASE_PREFIX.replace(os.path.sep, "."),
                               f.rsplit(".", 1)[0].replace(os.path.sep, "."))
            m = __import__(mn, {}, {}, "*")
            for n in dir(m):
                o = getattr(m, n)
                if (
                    inspect.isclass(o) and
                    issubclass(o, BaseCollector) and
                    o.__module__ == m.__name__
                ):
                    yield o
