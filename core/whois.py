# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# whois utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import urllib2
import socket
from collections import defaultdict
# NOC modules
import noc.lib.nosql  # noqa Connect to MongoDB
from noc.config import config
from noc.core.fileutils import urlopen
from noc.peer.models.whoisassetmembers import WhoisASSetMembers
from noc.peer.models.whoisoriginroute import WhoisOriginRoute

logger = logging.getLogger(__name__)


class WhoisCacheLoader(object):
    RIPE_AS_SET_MEMBERS = "https://ftp.ripe.net/ripe/dbase/split/ripe.db.as-set.gz"
    RIPE_ROUTE_ORIGIN = "https://ftp.ripe.net/ripe/dbase/split/ripe.db.route.gz"
    ARIN = "https://ftp.arin.net/pub/rr/arin.db"
    RADB = "ftp://ftp.radb.net/radb/dbase/radb.db.gz"

    to_cache = [ARIN, RADB]

    def __init__(
            self,
            use_ripe=config.peer.enable_ripe,
            use_arin=config.peer.enable_arin,
            use_radb=config.peer.enable_radb,
    ):
        self._url_cache = {}  # URL -> data
        self.status = True
        self.use_ripe = use_ripe
        self.use_arin = use_arin
        self.use_radb = use_radb

    @staticmethod
    def parse_rpsl(f, fields=None):
        obj = {}
        last = None
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                continue
            if line == "":
                # New object
                if obj:
                    yield obj
                    obj = {}
                continue
            if "#" in line:
                line, r = line.split("#", 1)
            if ":" in line:
                last = None
                k, v = [x.strip() for x in line.split(":", 1)]
                if fields and k not in fields:
                    continue
                v = [x.strip() for x in v.split(",")]
                if not v[-1]:
                    v.pop(-1)
                    last = k
                if k in obj:
                    obj[k] += v
                else:
                    obj[k] = v
            elif last:
                v = [x.strip() for x in line.split(",")]
                k = last
                last = None
                if not v[-1]:
                    v.pop(-1)
                    last = k
                obj[k] += v
        if obj:
            yield obj

    def urlopen(self, url):
        if url in self.to_cache:
            if url not in self._url_cache:
                f = urlopen(url, auto_deflate=True)
                self._url_cache[url] = f.read().splitlines()
                f.close()
            return self._url_cache[url]
        return urlopen(url, auto_deflate=True)

    def update_from_rpsl(self, url, r, key_field, values_field,
                         forward, parser):
        """
        Fetch RPSL file, parse and return a set of pairs (key, value),
        where key and value fields set by key_field and values_field parameters
        :param url: URL to download RPSL
        :param r: defaultdict(list)
        :param key_field: key field
        :param values_field: falue field
        :param forward: True for forward lookup, False otherwise
        :param parser:
        :return: Number of parsed items
        """
        if forward:
            def u(k, v):
                r[k] += [v]
        else:
            def u(k, v):
                r[v] += [k]

        n = 0
        logger.info("Loading %s", url)
        try:
            f = self.urlopen(url)
        except urllib2.URLError as e:
            logger.error("Failed to download %s: %s" % (url, e))
            self.status = False
            return 0
        except socket.error as e:
            logger.error("Failed to download %s: %s" % (url, e))
            self.status = False
            return 0
        logger.info("Parsing")
        for o in parser(f, [key_field, values_field]):
            if key_field in o and values_field in o:
                k = o[key_field][0].upper()
                for x in o[values_field]:
                    u(k, x.upper())
                    n += 1
        return n

    def process_as_set_members(self):
        """
        Update as-set -> members
        :return:
        """
        r = defaultdict(list)
        if self.use_ripe:
            logger.info("Processing RIPE as-set -> members")
            v = self.update_from_rpsl(
                self.RIPE_AS_SET_MEMBERS, r,
                "as-set", "members", True,
                self.parse_rpsl)
            logger.info("Processed RIPE as-set -> members: %d records" % v)
        if self.use_arin:
            logger.info("Processing ARIN as-set -> members")
            v = self.update_from_rpsl(
                self.ARIN, r,
                "as-set", "members", True,
                self.parse_rpsl)
            logger.info("Processed ARIN as-set -> members: %d records" % v)
        if self.use_radb:
            logger.info("Processing RADb as-set -> members")
            v = self.update_from_rpsl(
                self.RADB, r,
                "as-set", "members", True,
                self.parse_rpsl)
            logger.info("Processed RADb as-set -> members: %d records" % v)
        if r:
            # Upload to database
            logger.info("Updating noc.whois.asset.members collection")
            count = WhoisASSetMembers.upload(r)
            logger.info("%d records written into noc.whois.asset.members collection" % count)
        else:
            logger.info("Nothing to update")

    def process_origin_route(self):
        """
        Update origin -> route
        :return:
        """
        r = defaultdict(list)
        if self.use_ripe:
            logger.info("Processing RIPE origin -> route")
            v = self.update_from_rpsl(self.RIPE_ROUTE_ORIGIN, r,
                                      "route", "origin", False, self.parse_rpsl)
            logger.info("Processed RIPE origin -> route: %d records" % v)
        if self.use_arin:
            logger.info("Processing ARIN origin -> route")
            v = self.update_from_rpsl(self.ARIN, r,
                                      "route", "origin", False, self.parse_rpsl)
            logger.info("Processed ARIN origin -> route: %d records" % v)
        if self.use_radb:
            logger.info("Processing RADb origin -> route")
            v = self.update_from_rpsl(self.RADB, r,
                                      "route", "origin", False, self.parse_rpsl)
            logger.info("Processed RADb origin -> route: %d records" % v)
        if r:
            # Upload to database
            logger.info("Updating noc.whois.origin.route collection")
            count = WhoisOriginRoute.upload(r)
            logger.info("%d records written into noc.whois.origin.route collection" % count)

    def update(self):
        self.process_as_set_members()
        self.process_origin_route()
        return self.status


def update_whois_cache():
    loader = WhoisCacheLoader()
    loader.update()
