# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Distributed coordinated storage
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Third-party modules
import tornado.gen
import tornado.ioloop
from six.moves.urllib.parse import urlparse
## Python modules
from noc.core.handler import get_handler


class DCSBase(object):
    def __init__(self, url, ioloop=None):
        self.logger = logging.getLogger(__name__)
        self.url = url
        self.ioloop = ioloop or tornado.ioloop.IOLoop.current()
        self.parse_url(urlparse(url))

    def parse_url(self, u):
        pass

    def start(self):
        """
        Run IOLoop if not started yet
        :return: 
        """
        self.ioloop.start()

    def stop(self):
        """
        Stop IOLoop if not stopped yet
        :return: 
        """
        self.ioloop.stop()

    @tornado.gen.coroutine
    def register(self, name, address, port, pool=None, lock=None):
        """
        Register service
        :param name: 
        :param address: 
        :param port: 
        :param pool: 
        :param lock:
        :return: 
        """
        raise NotImplementedError()
