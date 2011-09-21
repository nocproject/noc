# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.update_whois_cache periodic task
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
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

    def parse_rpsl(self, f, fields=None):
        obj = {}
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
                k, v = [x.strip() for x in l.split(":", 1)]
                if fields and k not in fields:
                    continue
                if k in obj:
                    obj[k] += [v]
                else:
                    obj[k] = [v]
        if obj:
            yield obj

    def get_forward(self, url, key_field, values_field, parser):
        self.info("Processing %s" % url)
        r = {}
        f = urlopen(url,auto_deflate=True)
        for o in parser(f, [key_field, values_field]):
            if key_field in o and values_field in o:
                r[o[key_field][0].upper()] = [x.upper()
                                              for x in o[values_field]]
        return r

    def get_reverse(self, url, key_field, values_field, parser):
        self.info("Processing %s" % url)
        r = {}
        f = urlopen(url,auto_deflate=True)
        for o in parser(f, [key_field, values_field]):
            if key_field in o and values_field in o:
                k = o[key_field][0].upper()
                for v in o[values_field]:
                    v = v.upper()
                    try:
                        r[v] += [k]
                    except KeyError:
                        r[v] = [k]
        return r

    def execute(self):
        from noc.lib.nosql import get_db
        
        db = get_db()
        use_ripe = config.getboolean("peer", "whois_ripe")
        # Update as-set -> members
        r = {}
        if use_ripe:
            r_ripe = self.get_forward(self.RIPE_AS_SET_MEMBERS,
                                      "as-set", "members", self.parse_rpsl)
            r.update(r_ripe)
        if r:
            # Upload to database
            self.info("Updating noc.whois.asset.members collection")
            c = db.noc.whois.asset.members
            c.drop()
            c.insert([{"as_set": k, "members": r[k] } for k in r],
                manipulate=False, check_keys=False)
        # Update origin -> route
        r = {}
        if use_ripe:
            r_ripe = self.get_reverse(self.RIPE_ROUTE_ORIGIN,
                                      "route", "origin", self.parse_rpsl)
            r.update(r_ripe)
        if r:
            # Upload to database
            self.info("Updating noc.whois.origin.route collection")
            c = db.noc.whois.origin.route
            c.drop()
            c.insert([{"origin": k, "routes": r[k] } for k in r],
                manipulate=False, check_keys=False)
