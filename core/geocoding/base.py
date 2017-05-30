# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Base geocoding class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import namedtuple
# Third-party modules
import pycurl
import six


GeoCoderResult = namedtuple(
    "GeoCoderResult", ["exact", "query", "path", "lon", "lat"])


class GeoCoderError(Exception):
    pass


class GeoCoderLimitExceeded(GeoCoderError):
    pass


class BaseGeocoder(object):
    name = None

    def __init__(self, *args, **kwargs):
        pass

    def forward(self, query):
        """
        Forward lookup
        :param query: Address as string
        :return: GeoCoderResult or None
        """

    def get(self, url):
        """
        Perform get request
        :param url:
        :return:
        """
        buff = six.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buff)
        try:
            c.perform()
        except pycurl.error as e:
            raise GeoCoderError(str(e))
        finally:
            code = c.getinfo(c.RESPONSE_CODE)
            c.close()
        return code, buff.getvalue()

    @staticmethod
    def get_path(data, path):
        """
        Returns nested object referred by dot-separated path, or None
        :param data:
        :param path:
        :return:
        """
        o = data
        for p in path.split("."):
            if p in o:
                o = o[p]
            else:
                return None
        return o
