# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.update_whois_cache periodic task
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
from collections import defaultdict
## NOC modules
from noc.lib.periodic import Task as NOCTask
from noc.settings import config
from noc.lib.fileutils import urlopen


class Task(NOCTask):
    name = "peer.update_whois_cache"
    description = "Update whois cache"
    wait_for = ["cm.prefix_list_pull"]
    
    RIPE_AS_SET_MEMBERS = "ftp://ftp.ripe.net/ripe/dbase/split/ripe.db.as-set.gz"
    RIPE_ROUTE_ORIGIN = "ftp://ftp.ripe.net/ripe/dbase/split/ripe.db.route.gz"
    ARIN = "ftp://ftp.arin.net/pub/rr/arin.db"
    RADB = "ftp://ftp.radb.net/radb/dbase/radb.db.gz"
    
    to_cache = [ARIN, RADB]

    def parse_rpsl(self, f, fields=None):
        obj = {}
        last = None
        for l in f:
            l = l.strip()
            if l.startswith("#"):
                continue
            if l == "":
                # New object
                if obj:
                    yield obj
                    obj = {}
                continue
            if "#" in l:
                l, r = l.split("#", 1)
            if ":" in l:
                last = None
                k, v = [x.strip() for x in l.split(":", 1)]
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
                v = [x.strip() for x in l.split(",")]
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
        :return:
        """
        if forward:
            u = lambda k, v: r[k].append(v)
        else:
            u = lambda k, v: r[v].append(k)
        n = 0
        f = self.urlopen(url)
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
        from noc.peer.models.whoisassetmembers import WhoisASSetMembers

        r = defaultdict(list)
        if self.use_ripe:
            self.info("Processing RIPE as-set -> members")
            v = self.update_from_rpsl(self.RIPE_AS_SET_MEMBERS, r,
                                      "as-set", "members", True,
                                      self.parse_rpsl)
            self.info("Processed RIPE as-set -> members: %d records" % v)
        if self.use_arin:
            self.info("Processing ARIN as-set -> members")
            v = self.update_from_rpsl(self.ARIN, r,
                                      "as-set", "members", True,
                                      self.parse_rpsl)
            self.info("Processed ARIN as-set -> members: %d records" % v)
        if self.use_radb:
            self.info("Processing RADb as-set -> members")
            v = self.update_from_rpsl(self.RADB, r,
                                      "as-set", "members", True,
                                      self.parse_rpsl)
            self.info("Processed RADb as-set -> members: %d records" % v)
        if r:
            # Upload to database
            self.info("Updating noc.whois.asset.members collection")
            count = WhoisASSetMembers.upload(
                [{"as_set": k, "members": r[k]} for k in r]
            )
            self.info("%d records written into noc.whois.asset.members collection" % count)

    def process_origin_route(self):
        """
        Update origin -> route
        :return:
        """
        from noc.peer.models.whoisoriginroute import WhoisOriginRoute

        r = defaultdict(list)
        if self.use_ripe:
            self.info("Processing RIPE origin -> route")
            v = self.update_from_rpsl(self.RIPE_ROUTE_ORIGIN, r,
                                  "route", "origin", False, self.parse_rpsl)
            self.info("Processed RIPE origin -> route: %d records" % v)
        if self.use_arin:
            self.info("Processing ARIN origin -> route")
            v = self.update_from_rpsl(self.ARIN, r,
                                   "route", "origin", False, self.parse_rpsl)
            self.info("Processed ARIN origin -> route: %d records" % v)
        if self.use_radb:
            self.info("Processing RADb origin -> route")
            v = self.update_from_rpsl(self.RADB, r,
                                  "route", "origin", False, self.parse_rpsl)
            self.info("Processed RADb origin -> route: %d records" % v)
        if r:
            # Upload to database
            self.info("Updating noc.whois.origin.route collection")
            count = WhoisOriginRoute.upload(
                [{"origin": k, "routes": r[k]} for k in r]
            )
            self.info("%d records written into noc.whois.origin.route collection" % count)

    def execute(self):
        self._url_cache = {}  # URL -> data
        # Read config
        self.use_ripe = config.getboolean("peer", "use_ripe")
        self.use_arin = config.getboolean("peer", "use_arin")
        self.use_radb = config.getboolean("peer", "use_radb")
        # Process
        self.process_as_set_members()
        self.process_origin_route()
        return True
