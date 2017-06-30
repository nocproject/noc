# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Customized NSQ reader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import urlparse
import urllib
import logging
# Third-party modules
import tornado.gen
from nsq.reader import Reader as BaseReader, _utf8_params
import ujson
# NOC modules
from noc.core.http.client import fetch

logger = logging.getLogger(__name__)


class Reader(BaseReader):
    @tornado.gen.coroutine
    def query_lookupd(self):
        logger.info("query_lookupd")
        endpoint = self.lookupd_http_addresses[self.lookupd_query_index]
        self.lookupd_query_index = (self.lookupd_query_index + 1) % len(self.lookupd_http_addresses)

        # urlsplit() is faulty if scheme not present
        if "://" not in endpoint:
            endpoint = "http://" + endpoint

        scheme, netloc, path, query, fragment = urlparse.urlsplit(endpoint)

        if not path or path == "/":
            path = "/lookup"

        params = urlparse.parse_qs(query)
        params["topic"] = self.topic
        query = urllib.urlencode(_utf8_params(params), doseq=1)
        lookupd_url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))

        code, headers, body = yield fetch(
            lookupd_url,
            connect_timeout=self.lookupd_connect_timeout,
            request_timeout=self.lookupd_request_timeout
        )

        if not (200 <= code <= 299):
            logger.warning("[%s] lookupd %s query error: %s %s",
                           self.name, lookupd_url, code, body)
            return
        # Decode response
        try:
            lookup_data = ujson.loads(body)
        except ValueError as e:
            logger.warning("[%s] lookupd %s failed to parse JSON: %s",
                           self.name, lookupd_url, e)
            return

        if lookup_data["status_code"] != 200:
            logger.warning("[%s] lookupd %s responded with %d",
                           self.name, lookupd_url,
                           lookup_data["status_code"])
            return

        for producer in lookup_data["data"]["producers"]:
            # TODO: this can be dropped for 1.0
            address = producer.get("broadcast_address", producer.get("address"))
            assert address
            self.connect_to_nsqd(address, producer["tcp_port"])
