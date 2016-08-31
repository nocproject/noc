# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Configuration class
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import random
import logging
import urllib
## Third-party modules
import yaml

logger = logging.getLogger(__name__)


class BaseConfig(object):
    CONFIG = "etc/noc.yml"
    # config.noc attribute defaults
    DEFAULTS = {
        "user": "noc",
        "group": "noc",
        "installation_name": "Unconfigured installation",
        "timezone": "Europe/Moscow",
        "secret_key": None,
        # Mongo section
        "mongo_db": "noc",
        "mongo_user": "noc",
        "mongo_password": "noc",
        "mongo_rs": None,
        # Postgres section
        "pg_db": "noc",
        "pg_user": "noc",
        "pg_password": "noc",
        # InfluxDB section
        "influx_db": "noc",
        "topology_rca_window": 0
    }

    def __init__(self):
        self.services = {}
        #
        self.user = None
        self.group = None
        self.installation_name = None
        self.secret_key = None
        # Postgres section
        self.pg_db = None
        self.pg_user = None
        self.pg_password = None
        # Mongo section
        self.mongo_db = None
        self.mongo_user = None
        self.mongo_password = None
        self.mongo_rs = None
        # InfluxDB section
        self.influx_db = None
        # Cached values
        self._mongo_connection_args = None
        self._pg_connection_args = None
        #
        self.topology_rca_window = 0
        #
        self.load()

    def load(self):
        """
        Load/Reload config
        """
        logger.info("Loading config froom %s", self.CONFIG)
        with open(self.CONFIG) as f:
            data = yaml.load(f)
        self.services = data.get("services")
        # Reset caches
        self._mongo_connection_args = None
        self._pg_connection_args = None
        # Set up attributes and defaults
        cfg = data.get("config", {}).get("noc", {})
        for a in self.DEFAULTS:
            setattr(self, a, cfg.get(a, self.DEFAULTS[a]))

    def get_service(self, name, pool=None, limit=None):
        """
        Returns a list of <ip>:<port> for given service.
        if *limit* parameter is set returns random sample up to
        *limit* size
        """
        if pool:
            name = "%s-%s" % (name, pool)
        svc = self.services.get(name, [])
        if limit and svc:
            return random.sample(svc, min(limit, len(svc)))
        return svc

    @property
    def pg_connection_args(self):
        """
        PostgreSQL database connection arguments
        suitable to pass to psycopg2.connect
        """
        if not self._pg_connection_args:
            hosts = self.get_service("postgres", limit=1)
            if not hosts:
                hosts = ["127.0.0.1:5432"]
            host, port = hosts[0].split(":")
            self._pg_connection_args = {
                "host": host,
                "port": int(port),
                "database": self.pg_db,
                "user": self.pg_user,
                "password": self.pg_password
            }
        return self._pg_connection_args

    @property
    def mongo_connection_args(self):
        """
        Mongo connection arguments. Suitable to pass to
        pymongo.connect and mongoengine.connect
        """
        if not self._mongo_connection_args:
            self._mongo_connection_args = {
                "db": self.mongo_db,
                "username": self.mongo_user,
                "password": self.mongo_password,
                "socketKeepAlive": True
            }
            has_credentials = self.mongo_user or self.mongo_password
            if has_credentials:
                self._mongo_connection_args["authentication_source"] = self.mongo_db
            hosts = self.get_service("mongod", limit=5)
            if self.mongo_rs:
                self._mongo_connection_args["replicaSet"] = self.mongo_rs
                self._mongo_connection_args["slave_okay"] = True
            elif len(hosts) > 1:
                raise ValueError("Replica set name must be set")
            url = ["mongodb://"]
            if has_credentials:
                url += ["%s:%s@" % (urllib.quote(self.mongo_user),
                                    urllib.quote(self.mongo_password))]
            url += [",".join(hosts)]
            url += ["/%s" % self.mongo_db]
            self._mongo_connection_args["host"] = "".join(url)
        return self._mongo_connection_args


# Config singleton
config = BaseConfig()
