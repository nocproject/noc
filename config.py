# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NOC config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import urllib
import sys
import os
# NOC modules
from noc.core.config.base import BaseConfig, ConfigSection
from noc.core.config.params import (
    StringParameter, MapParameter, IntParameter, BooleanParameter,
    HandlerParameter, SecondsParameter, FloatParameter,
    ServiceParameter)


class Config(BaseConfig):
    pool = StringParameter()

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
    language = StringParameter(default="en")
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

    instance = IntParameter(default=0)
    listen = StringParameter(default="auto:0")

    class traceback(ConfigSection):
        reverse = BooleanParameter(default=True)

    class mongo(ConfigSection):
        addresses = ServiceParameter(service="mongo", wait=True)
        db = StringParameter(default="noc")
        user = StringParameter()
        password = StringParameter()
        rs = StringParameter()

    class pg(ConfigSection):
        addresses = ServiceParameter(
            service=["pgbouncer", "postgres"],
            wait=True
        )
        db = StringParameter(default="noc")
        user = StringParameter()
        password = StringParameter()

    class clickhouse(ConfigSection):
        addresses = ServiceParameter(service="clickhouse", wait=True)
        db = StringParameter(default="noc")
        user = StringParameter()
        password = StringParameter()

    class influxdb(ConfigSection):
        addresses = ServiceParameter(service="influxdb", wait=True)
        db = StringParameter(default="noc")
        user = StringParameter()
        password = StringParameter()

    class nsqlookupd(ConfigSection):
        addresses = ServiceParameter(service="nsqlookupd", wait=True)

    class nsqd(ConfigSection):
        addresses = ServiceParameter(service="nsqd",
                                     wait=True, near=True)

    class memcached(ConfigSection):
        addresses = ServiceParameter(service="memcached", wait=True)
        pool_size = IntParameter(default=8)
        default_ttl = IntParameter(default=86400)

    class cm(ConfigSection):
        vcs_path = StringParameter(default="/usr/local/bin/hg")
        repo = StringParameter(default="/var/repo")

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

    class geocoding(ConfigSection):
        order = StringParameter(default="yandex,google")
        yandex_key = StringParameter(default="")
        google_key = StringParameter(default="")
        google_language = StringParameter(default="en")

    class escalation(ConfigSection):
        global_limit = IntParameter(default=50)

    class audit(ConfigSection):
        command_ttl = SecondsParameter(default="1m")
        login_ttl = SecondsParameter(default="1m")
        reboot_ttl = SecondsParameter(default="0")
        config_ttl = SecondsParameter(default="1y")
        db_ttl = SecondsParameter(default="5y")

    class logging(ConfigSection):
        log_api_calls = BooleanParameter(default=False)
        log_sql_statements = BooleanParameter(default=False)

    class gridvcs(ConfigSection):
        config_mirror_path = StringParameter("")

    class path(ConfigSection):
        smilint = StringParameter()
        smidump = StringParameter()
        dig = StringParameter()

    class proxy(ConfigSection):
        http_proxy = StringParameter(default=os.environ.get("http_proxy"))
        https_proxy = StringParameter(default=os.environ.get("https_proxy"))
        ftp_proxy = StringParameter(default=os.environ.get("ftp_proxy"))

    class login(ConfigSection):
        methods = StringParameter(default="local")
        session_ttl = SecondsParameter(default="7d")
        restrict_to_group = StringParameter(default="")
        single_session_group = StringParameter(default="")
        mutual_exclusive_group = StringParameter(default="")
        idle_timeout = SecondsParameter(default="1w")

    class ping(ConfigSection):
        max_packets = IntParameter(default=3)
        timeout = IntParameter(default=2)
        throttle_threshold = FloatParameter()
        restore_threshold = FloatParameter()
        tos = IntParameter(
            min=0, max=255,
            default=0
        )

    class activator(ConfigSection):
        tos = IntParameter(
            min=0, max=255,
            default=0
        )

    class sync(ConfigSection):
        config_ttl = SecondsParameter(default="1d")
        ttl_jitter = FloatParameter(default=0.1)
        expired_refresh_timeout = IntParameter(default=25)
        expired_refresh_chunk = IntParameter(default=100)

    class pmwriter(ConfigSection):
        batch_size = IntParameter(default=2500)
        metrics_buffer = IntParameter(default=50000)
        read_from = StringParameter(default="pmwriter")
        write_to = StringParameter(default="influxdb")

    class chwriter(ConfigSection):
        batch_size = IntParameter(default=50000)
        records_buffer = IntParameter(default=1000000)
        batch_delay_ms = IntParameter(default=1000)
        channel_expire_interval = IntParameter(default=300)

    class web(ConfigSection):
        api_row_limit = IntParameter(default=0)
        language = StringParameter(default="en")
        install_collection = BooleanParameter(default=False)
        max_threads = IntParameter(default=10)

    class cache(ConfigSection):
        vcinterfacescount = SecondsParameter(default="1h")
        vcprefixes = SecondsParameter(default="1h")
        cache_class = StringParameter(default="noc.core.cache.mongo.MongoCache")
        default_ttl = IntParameter(default=86400)
        pool_size = IntParameter(default=8)

    class dns(ConfigSection):
        warn_before_expired = SecondsParameter(default="30d")

    class scheduler(ConfigSection):
        max_threads = IntParameter(default=20)

    class sae(ConfigSection):
        db_threads = IntParameter(default=20)

    class classifier(ConfigSection):
        lookup_handler = HandlerParameter(
            default="noc.services.classifier.rulelookup.RuleLookup")
        default_interface_profile = StringParameter(default="default")

    class discovery(ConfigSection):
        max_threads = IntParameter(default=20)

    class correlator(ConfigSection):
        max_threads = IntParameter(default=20)
        topology_rca_window = IntParameter(default=0)

    class syslogcollector(ConfigSection):
        listen = StringParameter(default="0.0.0.0:514")

    class trapcollector(ConfigSection):
        listen = StringParameter(default="0.0.0.0:162")

    class escalator(ConfigSection):
        max_threads = IntParameter(default=10)

    class sentry(ConfigSection):
        url = StringParameter(default="")

    class mailsender(ConfigSection):
        smtp_server = StringParameter()
        smtp_port = IntParameter(default=25)
        use_tls = BooleanParameter(default=False)
        helo_hostname = StringParameter(default="noc")
        from_address = StringParameter(default="noc@example.com")
        smtp_user = StringParameter()
        smtp_password = StringParameter()

    def __init__(self):
        self.setup_logging()

    @property
    def pg_connection_args(self):
        """
        PostgreSQL database connection arguments
        suitable to pass to psycopg2.connect
        """
        return {
            "host": self.pg.addresses[0].host,
            "port": self.pg.addresses[0].port,
            "database": self.pg.db,
            "user": self.pg.user,
            "password": self.pg.password
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
            hosts = self.mongo.addresses
            if self.mongo.rs:
                self._mongo_connection_args["replicaSet"] = self.mongo.rs
                self._mongo_connection_args["slave_okay"] = True
            elif len(hosts) > 1:
                raise ValueError("Replica set name must be set")
            url = ["mongodb://"]
            if has_credentials:
                url += ["%s:%s@" % (urllib.quote(self.mongo.user),
                                    urllib.quote(self.mongo.password))]
            url += [",".join(str(h) for h in hosts)]
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
config.setup_logging()
