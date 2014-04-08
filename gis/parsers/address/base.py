# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Parse and load FIAS data
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
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