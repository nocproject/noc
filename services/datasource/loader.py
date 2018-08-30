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
from noc.config import config

BASE_PREFIX = os.path.join("services", "datasource", "datasources")
PATHS = config.get_customized_paths(BASE_PREFIX)

# ds name -> ds cls
DS_MAP = {}


def get_datasource(name):
    global DS_MAP

    if not DS_MAP:
        load_datasources()
    return DS_MAP.get(name)


def load_datasources():
    global DS_MAP, PATHS, BASE_PREFIX

    for path in PATHS:
        if not os.path.exists(path):
            continue
        b, _ = path.split(BASE_PREFIX)
        for f in os.listdir(path):
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
                    issubclass(o, BaseDataSource) and
                    o.__module__ == m.__name__
                ):
                    DS_MAP[o.name] = o
                    break
