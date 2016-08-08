# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Load config from environment
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import urlparse
import os
## NOC modules
from base import BaseProtocol


class EnvProtocol(BaseProtocol):
    """
    Environment variables mapping
    URL:
        env:///<prefix>
    Maps config.my.variable to <prefix>_MY_VARIABLE
    """

    def __init__(self, config, url):
        super(EnvProtocol, self).__init__(config, url)
        c = urlparse.urlparse(url)
        self.prefix = c.path[1:]

    def load(self):
        for v in self.config:
            env_name = "%s_%s" % (
                self.prefix,
                v.upper().replace(".", "_")
            )
            ev = os.environ.get(env_name)
            if ev is not None:
                self.config.set_parameter(v, ev)

    def dump(self):
        for v in self.config:
            env_name = "%s_%s" % (
                self.prefix,
                v.upper().replace(".", "_")
            )
            v = self.config.get_parameter(v)
            if v is not None:
                print "%s=%s" % (env_name, v)
