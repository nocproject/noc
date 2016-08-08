# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC config
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import urllib
import sys
## NOC modules
from noc.core.config.base import BaseConfig, ConfigSection
from noc.core.config.params import (StringParameter, MapParameter,
                                    IntParameter, BooleanParameter,
                                    HandlerParameter, SecondsParameter)


class Config(BaseConfig):
    pool = StringParameter(default="global")

    loglevel = MapParameter(default="info", mappings={
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG
    })
    log_format = StringParameter(
        default="%(asctime)s [%(name)s] %(message)s"
    )
    installation_name = StringParameter(
        default="Unconfigured installation"
    )
    language_code = StringParameter(
        default="en-us"
    )
    timezone = StringParameter(
        default="Europe/Moscow"
    )
    date_format = StringParameter(
        default="d.m.Y"
    )
    time_format = StringParameter(
        default="H:i:s"
    )
    month_day_format = StringParameter(
        default="F j"
    )
    year_month_format = StringParameter(
        default="F Y"
    )
    datetime_format = StringParameter(
        default="d.m.Y H:i:s"
    )
    secret_key = StringParameter(default="12345")

    mirror_path = StringParameter(default="/opt/noc/var/config_mirror")

    class mongo(ConfigSection):
        host = StringParameter(default="mongo-master")
        port = IntParameter(
            min=1, max=65535,
            default=27017
        )
        db = StringParameter(default="noc")
        user = StringParameter()
        password = StringParameter()
        rs = StringParameter()

    class pg(ConfigSection):
        db_engine = StringParameter(
            default="django.db.backends.postgresql_psycopg2"
        )
        host = StringParameter(default="pg-master")
        port = IntParameter(
            min=1, max=65535,
            default=5432
        )
        db = StringParameter(default="noc")
        user = StringParameter()
        password = StringParameter()
        db_options = {}

    class clickhouse(ConfigSection):
        host = StringParameter(default="clickhouse-master")
        port = IntParameter(
            min=1, max=65535,
            default=8123
        )
        db = StringParameter(default="noc")
        user = StringParameter()
        password = StringParameter()

    class customization(ConfigSection):
        favicon = StringParameter(
            default="/static/img/logo_24x24_deep_azure.png"
        )
        logo_url = StringParameter(
            default="/static/img/logo_white.svg"
        )
        logo_width = IntParameter(default=24)
        logo_height = IntParameter(default=24)
        branding_color = StringParameter(
            default="#ffffff"
        )
        branding_background_color = StringParameter(
            default="#34495e"
        )

    class rpc(ConfigSection):
        retry_timeout = StringParameter(
            default="0.1,0.5,1,3,10,30"
        )

    class gis(ConfigSection):
        ellipsoid = StringParameter(default="ПЗ-90")
        enable_osm = BooleanParameter(default=True)
        enable_google_sat = BooleanParameter(default=False)
        enable_google_roadmap = BooleanParameter(default=False)

    class audit(ConfigSection):
        command_ttl = SecondsParameter(default="1m")
        login_ttl = SecondsParameter(default="1m")
        reboot_ttl = SecondsParameter(default="0")
        config_ttl = SecondsParameter(default="1y")
        db_ttl = SecondsParameter(default="5y")

    class login(ConfigSection):
        method = HandlerParameter(
            default="noc.services.login.backends.local.LocalBackend"
        )
        session_ttl = SecondsParameter(default="7d")

    class ping(ConfigSection):
        tos = IntParameter(
            min=0, max=255,
            default=0
        )

    class pmwriter(ConfigSection):
        batch_size = IntParameter(default=1000)
        metrics_buffer = IntParameter(default=4000)

    def __init__(self):
        self.setup_logging()

    def use_pg_pool(self):
        self.pg.db_engine = "dbpool.db.backends.postgresql_psycopg2"
        self.pg.db_options.update({
            "MAX_CONNS": 1,
            "MIN_CONNS": 1
        })

    @property
    def pg_connection_args(self):
        """
        PostgreSQL database connection arguments
        suitable to pass to psycopg2.connect
        """
        return {
            "host": self.pg.host,
            "port": self.pg.port,
            "database": self.pg.db,
            "user": self.pg.user,
            "password": self.pg_password
        }

    @property
    def mongo_connection_args(self):
        """
        Mongo connection arguments. Suitable to pass to
        pymongo.connect and mongoengine.connect
        """
        if not hasattr(self, "_mongo_connection_args"):
            self._mongo_connection_args = {
                "db": self.mongo.db,
                "username": self.mongo.user,
                "password": self.mongo.password,
                "socketKeepAlive": True
            }
            has_credentials = self.mongo.user or self.mongo.password
            if has_credentials:
                self._mongo_connection_args["authentication_source"] = self.mongo.db
            hosts = [self.mongo.host]
            if self.mongo.rs:
                self._mongo_connection_args["replicaSet"] = self.mongo.rs
                self._mongo_connection_args["slave_okay"] = True
            elif len(hosts) > 1:
                raise ValueError("Replica set name must be set")
            url = ["mongodb://"]
            if has_credentials:
                url += ["%s:%s@" % (urllib.quote(self.mongo.user),
                                    urllib.quote(self.mongo.password))]
            url += [",".join(hosts)]
            url += ["/%s" % self.mongo.db]
            self._mongo_connection_args["host"] = "".join(url)
        return self._mongo_connection_args

    def setup_logging(self, loglevel=None):
        """
        Create new or setup existing logger
        """
        if not loglevel:
            loglevel = self.loglevel
        logger = logging.getLogger()
        if len(logger.handlers):
            # Logger is already initialized
            fmt = logging.Formatter(self.log_format, None)
            for h in logging.root.handlers:
                if isinstance(h, logging.StreamHandler):
                    h.stream = sys.stdout
                h.setFormatter(fmt)
            logging.root.setLevel(loglevel)
        else:
            # Initialize logger
            logging.basicConfig(
                stream=sys.stdout,
                format=self.log_format,
                level=loglevel
            )
        logging.captureWarnings(True)


config = Config()
config.load()
