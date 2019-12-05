# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BaseGeocoder class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from collections import namedtuple

# NOC modules
from noc.core.http.client import fetch_sync
from .errors import GeoCoderError


GeoCoderResult = namedtuple("GeoCoderResult", ["exact", "query", "path", "lon", "lat"])


class BaseGeocoder(object):
    name = None

    def __init__(self, *args, **kwargs):
        pass

    def forward(self, query):
        """
        Forward lookup
        :param query: Address as string
        :type query: str
        :return: GeoCoderResult or None
        """

    def get(self, url):
        """
        Perform get request
        :param url:
        :type url: str
        :return:
        """
        code, headers, body = fetch_sync(
            url, follow_redirects=True, validate_cert=False, allow_proxy=True
        )
        if 200 <= code <= 299:
            return code, body
        else:
            raise GeoCoderError("HTTP Error %s" % code)

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
