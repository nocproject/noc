# ----------------------------------------------------------------------
# whois utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from collections import defaultdict
from urllib.error import URLError
from io import TextIOWrapper

# NOC modules
from noc.config import config
from noc.core.fileutils import urlopen
from noc.peer.models.whoisassetmembers import WhoisASSetMembers
from noc.peer.models.whoisoriginroute import WhoisOriginRoute
from noc.peer.models.asn import AS
from noc.core.scheduler.job import Job
from noc.core.mongo.connection import connect

logger = logging.getLogger(__name__)

IGNORED_LINES = {" " * 16}  # 16 - default tab, Add after find:
# 'descr:          Honest,',
# '                ',
# '                299 Broadway',


class WhoisCacheLoader(object):
    RIPE_AS_SET_MEMBERS = "https://ftp.ripe.net/ripe/dbase/split/ripe.db.as-set.gz"
    RIPE_ROUTE_ORIGIN = "https://ftp.ripe.net/ripe/dbase/split/ripe.db.route.gz"
    ARIN = "https://ftp.arin.net/pub/rr/arin.db.gz"
    RADB = "ftp://ftp.radb.net/radb/dbase/radb.db.gz"

    to_cache = [ARIN, RADB]

    JCLS_WHOIS_PREFIX = "noc.services.discovery.jobs.as.job.ASDiscoveryJob"
    PER_AS_DELAY = 10

    class DownloadError(IOError):
        pass

    def __init__(
        self,
        use_ripe=config.peer.enable_ripe,
        use_arin=config.peer.enable_arin,
        use_radb=config.peer.enable_radb,
    ):
        self._url_cache = {}  # URL -> data
        self.use_ripe = use_ripe
        self.use_arin = use_arin
        self.use_radb = use_radb
        self._connected = False

    def require_db_connect(self):
        if self._connected:
            return
        connect()
        self._connected = True

    @staticmethod
    def parse_rpsl(f, fields=None):
        def q(s):
            """
            Sometimes, no-brake space symbol (\xa0) occures in whois database
            :param s: Source line
            :return: Cleaned string
            """
            return s.replace("\xa0", "").strip()

        obj = {}
        last = None
        for line in f:
            if line in IGNORED_LINES:
                continue
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
                k, v = [q(x) for x in line.split(":", 1)]
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
                f = TextIOWrapper(urlopen(url, auto_deflate=True), errors="ignore")
                self._url_cache[url] = f.read().splitlines()
                f.close()
            return self._url_cache[url]
        return TextIOWrapper(urlopen(url, auto_deflate=True), errors="ignore")

    def update_from_rpsl(self, url, r, key_field, values_field, forward, parser):
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
        except URLError as e:
            logger.error("Failed to download %s: %s" % (url, e))
            raise self.DownloadError("Failed to download %s: %s" % (url, e))
        except OSError as e:
            logger.error("Failed to download %s: %s" % (url, e))
            raise self.DownloadError("Failed to download %s: %s" % (url, e))
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
                self.RIPE_AS_SET_MEMBERS, r, "as-set", "members", True, self.parse_rpsl
            )
            logger.info("Processed RIPE as-set -> members: %d records" % v)
        if self.use_arin:
            logger.info("Processing ARIN as-set -> members")
            v = self.update_from_rpsl(self.ARIN, r, "as-set", "members", True, self.parse_rpsl)
            logger.info("Processed ARIN as-set -> members: %d records" % v)
        if self.use_radb:
            logger.info("Processing RADb as-set -> members")
            v = self.update_from_rpsl(self.RADB, r, "as-set", "members", True, self.parse_rpsl)
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
        # Get AS with discovered routes
        discoverable_as = {
            "AS%s" % a.asn
            for a in AS.objects.all()
            if a.profile.enable_discovery_prefix_whois_route and a.profile
        }
        # as -> [(prefix, description)]
        as_routes = defaultdict(list)
        if discoverable_as:
            logger.info(
                "Collecting prefix discovery information for AS: %s",
                ", ".join(a for a in discoverable_as),
            )

            def parser(f, fields=None):
                for obj in self.parse_rpsl(f):
                    if obj and "route" in obj and "origin" in obj:
                        origin = obj["origin"][0]
                        if origin in discoverable_as:
                            as_routes[origin] += [
                                (
                                    obj["route"][0],
                                    "\n".join(obj["descr"]) if "descr" in obj else None,
                                )
                            ]
                    yield obj

        else:
            parser = self.parse_rpsl
        r = defaultdict(list)
        if self.use_ripe:
            logger.info("Processing RIPE origin -> route")
            v = self.update_from_rpsl(self.RIPE_ROUTE_ORIGIN, r, "route", "origin", False, parser)
            logger.info("Processed RIPE origin -> route: %d records" % v)
        if self.use_arin:
            logger.info("Processing ARIN origin -> route")
            v = self.update_from_rpsl(self.ARIN, r, "route", "origin", False, parser)
            logger.info("Processed ARIN origin -> route: %d records" % v)
        if self.use_radb:
            logger.info("Processing RADb origin -> route")
            v = self.update_from_rpsl(self.RADB, r, "route", "origin", False, parser)
            logger.info("Processed RADb origin -> route: %d records" % v)
        if r:
            # Upload to database
            logger.info("Updating noc.whois.origin.route collection")
            self.require_db_connect()
            count = WhoisOriginRoute.upload(r)
            logger.info("%d records written into noc.whois.origin.route collection" % count)
        if as_routes:
            self.require_db_connect()
            delay = 0
            for a in as_routes:
                logger.info("[%s] Sending %d prefixes to AS discovery", a, len(as_routes[a]))
                Job.submit(
                    "scheduler",
                    self.JCLS_WHOIS_PREFIX,
                    key=AS.get_by_asn(int(a[2:])).id,
                    delta=delay,
                    data={"whois_route": as_routes[a]},
                )
                delay += self.PER_AS_DELAY

    def update(self):
        self.process_as_set_members()
        self.process_origin_route()


def update_whois_cache():
    loader = WhoisCacheLoader()
    loader.update()
