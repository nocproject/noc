# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Global HTTP Client setup
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
# Third-party modules
import tornado.httpclient

logger = logging.getLogger(__name__)


def setup_httpclient():
    try:
        import pycurl
    except ImportError:
        pycurl = None

    if pycurl:
        logger.info("Using curl http client")
        tornado.httpclient.AsyncHTTPClient.configure(
            "tornado.curl_httpclient.CurlAsyncHTTPClient"
        )
    else:
        logger.info("Using tornado http client")


setup_httpclient()
