# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various logging utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging


class PrefixLoggerAdapter(logging.LoggerAdapter):
    """
    Add [prefix] to log message
    """
    def __init__(self, logger, prefix, extra={}):
        self.pattern = "[%s] %%s" % prefix
        super(PrefixLoggerAdapter, self).__init__(logger, extra)

    def process(self, msg, kwargs):
        return self.pattern % msg, kwargs
