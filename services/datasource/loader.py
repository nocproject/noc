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
from noc.config import config

PATHS = [
    ("noc", "services/datasource/datasources"),
    (config.path.custom_path, "services/datasource/datasources")
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

    for base_path, local_path in PATHS:
        if not base_path:
            continue
        path = local_path
        if base_path != "noc":
            path = os.path.join(base_path, local_path)
        if not os.path.exists(path):
            continue
        for f in os.listdir(path):
            if not f.endswith(".py") or f.startswith("_") or f == "base.py":
                continue
            mn = "%s.%s.%s" % (os.path.basename(base_path),
                               local_path.replace("/", "."),
                               f.rsplit(".", 1)[0].replace("/", "."))
            print mn
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
