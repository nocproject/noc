# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# JSON loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os

# Third-party modules
import ujson


def iter_json_loader(dirs):
    """
    Iterate over collections and return list of (path, data) pairs
    :param dirs: colon-separated paths or list of dirs
    :return:
    """
    if not isinstance(dirs, list):
        dirs = dirs.split(":")
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for root, dirs, files in os.walk(d):
            for fn in files:
                if not fn.endswith(".json") or fn.startswith("."):
                    continue
                path = os.path.join(root, fn)
                if not os.path.isfile(path):
                    continue
                with open(path) as f:
                    data = ujson.loads(f.read())
                if not isinstance(data, list):
                    data = [data]
                for i in data:
                    yield path, i


def json_loader(dirs):
    return list(iter_json_loader(dirs))
