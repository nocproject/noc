# ----------------------------------------------------------------------
# Customized NSQ reader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from urllib.parse import urlencode, urlsplit, parse_qs, urlunsplit

# Third-party modules
from nsq.reader import Reader as BaseReader, _utf8_params
import orjson

# NOC modules
from noc.core.http.client import fetch
from noc.core.perf import metrics

logger = logging.getLogger(__name__)


class Reader(BaseReader):
    async def query_lookupd(self):
        logger.info("query_lookupd")
        endpoint = self.lookupd_http_addresses[self.lookupd_query_index]
        self.lookupd_query_index = (self.lookupd_query_index + 1) % len(self.lookupd_http_addresses)

        # urlsplit() is faulty if scheme not present
        if "://" not in endpoint:
            endpoint = "http://" + endpoint

        scheme, netloc, path, query, fragment = urlsplit(endpoint)

        if not path or path == "/":
            path = "/lookup"

        params = parse_qs(query)
        params["topic"] = self.topic
        query = urlencode(_utf8_params(params), doseq=True)
        lookupd_url = urlunsplit((scheme, netloc, path, query, fragment))

        code, headers, body = await fetch(
            lookupd_url,
            headers={"Accept": "application/vnd.nsq; version=1.0"},
            connect_timeout=self.lookupd_connect_timeout,
            request_timeout=self.lookupd_request_timeout,
        )

        if not 200 <= code <= 299:
            metrics["error", ("type", "nsqlookupd_query_error_code %s" % code)] += 1
            logger.warning("[%s] lookupd %s query error: %s %s", self.name, lookupd_url, code, body)
            return
        # Decode response
        try:
            lookup_data = orjson.loads(body)
        except ValueError as e:
            metrics["error", ("type", "nsqlookupd_invalid_json")] += 1
            logger.warning("[%s] lookupd %s failed to parse JSON: %s", self.name, lookupd_url, e)
            return

        if "data" in lookup_data:
            # Pre 1.0.0-compat
            producers = lookup_data["data"]["producers"]
        else:
            # 1.0.0-compat
            producers = lookup_data["producers"]
        for producer in producers:
            address = producer.get("broadcast_address", producer.get("address"))
            assert address
            self.connect_to_nsqd(address, producer["tcp_port"])
