# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Loader base class
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class BaseProtocol(object):
    def __init__(self, config, url):
        self.config = config
        self.url = url

    def load(self):
        raise NotImplementedError()

    def dump(self):
        raise NotImplementedError()
