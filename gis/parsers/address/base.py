# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Parse and load address data
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import gzip
import os
## Third-party modules
import requests
## NOC modules
from noc.gis.models.division import Division


class AddressParser(object):
    name = "Unknown"
    # Top-level object
    TOP_NAME = None

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts

    def info(self, msg):
        print "[%s] %s" % (self.name, msg)

    def error(self, msg):
        print "[%s: ERROR] %s" % (self.name, msg)

    def get_top(self):
        rf = Division.objects.filter(type="A", name=self.TOP_NAME).first()
        if rf:
            return rf
        self.info("Creating %s" % self.TOP_NAME)
        rf = Division(type="A", name=self.TOP_NAME)
        rf.save()
        return rf

    def download(self):
        return True

    def sync(self):
        pass

    def download_file(self, url, path, auto_deflate=False):
        self.info("Downloading %s" % url)
        r = requests.get(url, stream=True)
        size = int(r.headers["content-length"])
        chunk_size = 4 * 1024 * 1024
        self.info("    .... %d bytes" % size)
        with open(path, "w") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    f.flush()
        if auto_deflate:
            o = os.path.splitext(path)[0]
            with gzip.open(path, "rb") as f:
                with open(o, "w") as ff:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        ff.write(chunk)
            os.unlink(path)
