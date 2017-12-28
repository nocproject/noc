# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Monitoring endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import string
import tornado.web
import ujson

TR = string.maketrans(".-\"", "___")


class MonRequestHandler(tornado.web.RequestHandler):
    """
    Response with general purpose monitoring data
    """

    def initialize(self, service):
        self.service = service

    def get(self):
        """
        Resolves tuples from metrics name and responds with json
        :return:
        """
        mdata = self.service.get_mon_data()
        response = {}
        for key in mdata:
            if isinstance(key, tuple):
                metric_name = key[0]
                for k in key[1:]:
                    metric_name += "_" + "_".join(str(i) for i in k)
            else:
                metric_name = key.lower()
            cleared_name = str(metric_name).translate(TR)
            response[cleared_name] = mdata[key]
        self.write(
            ujson.dumps(response)
        )
