# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Load config from environment
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import os
# NOC modules
from base import BaseProtocol


class EnvProtocol(BaseProtocol):
    """
    Environment variables mapping
    URL:
        env:///<prefix>
    Maps config.my.variable to <prefix>_MY_VARIABLE
    """

    def load(self):
        prefix = self.parsed_url.path[1:]
        for v in self.config:
            env_name = "%s_%s" % (
                prefix,
                v.upper().replace(".", "_")
            )
            ev = os.environ.get(env_name)
            if ev is not None:
                self.config.set_parameter(v, ev)

    def dump(self):
        prefix = self.parsed_url[1:]
        for v in self.config:
            env_name = "%s_%s" % (
                prefix,
                v.upper().replace(".", "_")
            )
            v = self.config.dump_parameter(v)
            if v is not None:
                print("%s=%s" % (env_name, v))
