# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# DataSource loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import inspect
# NOC modules
from .datasources.base import BaseDataSource

PATHS = [
    "services/datasource/datasources",
    "custom/services/datasource/datasources",
]

# ds name -> ds cls
DS_MAP = {}


def get_datasource(name):
    global DS_MAP

    if not DS_MAP:
        load_datasources()
    return DS_MAP.get(name)


def load_datasources():
    global DS_MAP, PATHS

    for path in PATHS:
        if not os.path.exists(path):
            continue
        for f in os.listdir(path):
            if not f.endswith(".py") or f.startswith("_") or f == "base.py":
                continue
            mn = "noc.%s.%s" % (path.replace("/", "."), f.rsplit(".", 1)[0].replace("/", "."))
            m = __import__(mn, {}, {}, "*")
            for n in dir(m):
                o = getattr(m, n)
                if (
                    inspect.isclass(o) and
                    issubclass(o, BaseDataSource) and
                    o.__module__ == m.__name__
                ):
                    DS_MAP[o.name] = o
                    break
