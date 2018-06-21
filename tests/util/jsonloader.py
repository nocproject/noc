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
from fs import open_fs


def iter_json_loader(urls):
    """
    Iterate over collections and return list of (path, data) pairs
    :param urls: List of pyfilesystem URLs
    :return:
    """
    if not urls:
        urls = []
    for url in urls:
        with open_fs(url) as fs:
            for path in fs.walk.files(filter=["*.json"]):
                with fs.open(path) as f:
                    data = ujson.loads(f.read())
                if not isinstance(data, list):
                    data = [data]
                for i in data:
                    yield path, i


def json_loader(dirs):
    return list(iter_json_loader(dirs))
