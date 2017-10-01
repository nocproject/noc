# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# DatasourceRequestHandler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
import tornado.web
import cachetools
import threading
import operator
# NOC modules
from noc.config import config
from .loader import get_datasource

ds_lock = threading.Lock()


class DataSourceRequestHandler(tornado.web.RequestHandler):
    _cache = {}

    def initialize(self, service):
        self.service = service

    def get(self, path, *args, **kwargs):
        ds_name, fmt = path.rsplit(".", 1)
        writer = getattr(self, "write_%s" % fmt, None)
        if not writer:
            raise tornado.web.HTTPError(400, "Invalid format %s" % fmt)
        ds_cls = self.get_datasource(ds_name)
        if not ds_cls:
            raise tornado.web.HTTPError(404, "DataSource not found")
        ds = ds_cls()
        executor = self.service.get_executor("max")
        data = yield executor.submit(ds.get)
        writer(data)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_cache"),
                             lock=lambda _: ds_lock)
    def get_datasource(cls, name):
        return get_datasource(name)

    def write_tsv(self, data):
        """
        Write data in Tab-separated format
        :param data:
        :return:
        """
        self.set_header("Content-Type", "text/tsv;charset=utf-8")
        self.write(data)

    def write_csv(self, data):
        """
        Write data in comma-separated format
        :param data:
        :return:
        """
        raise NotImplementedError()
