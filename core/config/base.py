# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Configuration class
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import logging
import urllib
import sys

logger = logging.getLogger(__name__)

E = os.environ.get


def _get_seconds(v):
    m = 1
    if v.endswith("h"):
        v = v[:-1]
        m = 3600
    elif v.endswith("d"):
        v = v[:-1]
        m = 24 * 3600
    elif v.endswith("w"):
        v = v[:-1]
        m = 7 * 24 * 3600
    elif v.endswith("m"):
        v = v[:-1]
        m = 30 * 24 * 3600
    elif v.endswith("y"):
        v = v[:-1]
        m = 365 * 24 * 3600
    try:
        v = int(v)
    except ValueError:
        raise "Invalid expiration option in %s" % v
    return v * m

def _get_bool(v):
    v = v.lower()


class BaseConfig(object):
    LOG_LEVELS = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG
    }

    env = E("NOC_ENV", "test")
    loglevel = E("NOC_LOGLEVEL", "info")
    log_format = E("NOC_LOG_FORMAT", "%(asctime)s [%(name)s] %(message)s")
    installation_name = E("NOC_INSTALLATION_NAME",
                          "Unconfigured installation")
    language_code = E("NOC_LANGUAGE_CODE", "en-us")
    timezone = E("NOC_TIMEZONE", "Europe/Moscow")
    language = E("NOC_LANGUAGE", "en")
    secret_key = E("NOC_SECRET_KEY", "12345")
    date_format = E("NOC_DATE_FORMAT", "d.m.Y")
    time_format = E("NOC_TIME_FORMAT", "H:i:s")
    month_day_format = E("NOC_MONTH_DAY_FORMAT", "F j")
    year_month_format = E("NOC_YEAR_MONTH_FORMAT", "F Y")
    datetime_format = E("NOC_DATETIME_FORMAT", "d.m.Y H:i:s")
    listen = E("NOC_LISTEN", "0.0.0.0:1200")
    instance = E("NOC_INSTANCE", 0)
    #
    crashinfo_limit = int(E("NOC_CRASHINFO_LIMIT", 1000000))
    traceback_reverse = E("NOC_TRACEBACK_ORDER", "reverse") == "reverse"
    rpc_retry_timeout = E("NOC_RPC_RETRY_TIMEOUT", "0.1,0.5,1,3,10,30")
    db_threads = E("NOC_DB_THREADS", 10)
    discovery_max_threads = E("NOC_DISCOVERY_MAX_THREADS", 10)
    scheduler_max_threads = E("NOC_SCHEDULER_MAX_THREADS", 10)
    global_n_instances = E("NOC_global_n_instances", 1)
    # Mongo section
    mongo_host = E("NOC_MONGO_HOST", "mongo-master.%s" % env)
    mongo_db = E("NOC_MONGO_DB", "noc")
    mongo_user = E("NOC_MONGO_USER", "noc")
    mongo_password = E("NOC_MONGO_PASSWORD", "noc")
    mongo_rs = E("NOC_MONGO_RS", None)
    # Posgres section
    pg_db_engine = "django.db.backends.postgresql_psycopg2"
    pg_db_options = {}
    pg_host = E("NOC_PG_HOST", "postgres-master.%s" % env)
    pg_port = 5432
    pg_db = E("NOC_PG_DB", "noc")
    pg_user = E("NOC_PG_USER", "noc")
    pg_password = E("NOC_PG_PASSWORD", "noc")
    # Pooled processes
    pool = E("NOC_POOL", "global")
    #
    audit_command_ttl = _get_seconds(E("NOC_AUDIT_COMMAND_TTL", "1m"))
    audit_login_ttl = _get_seconds(E("NOC_AUDIT_LOGIN_TTL", "1m"))
    audit_reboot_ttl = _get_seconds(E("NOC_AUDIT_REBOOT_TTL", "0"))
    audit_config_ttl = _get_seconds(E("NOC_AUDIT_CONFIG_TTL", "1y"))
    audit_db_ttl = _get_seconds(E("NOC_AUDIT_DB_TTL", "5y"))
    #
    api_row_limit = int(E("NOC_API_ROW_LIMIT", 0))
    #
    gis_ellipsoid = E("NOC_GIS_ELLIPSOID", "ПЗ-90")
    #
    config_mirror_path = E("NOC_CONFIG_MIRROR_PATH")

    # sync
    sync_config_ttl = E("NOC_SYNC_CONFIG_TTL", 86400)
    sync_ttl_jitter = E("NOC_SYNC_TTL_JITTER", 0.1)
    sync_expired_refresh_timeout = E("NOC_SYNC_REFRESH_TIMEOUT", 25)
    sync_expired_refresh_chunk = E("NOC_SYNC_REFRESH_CHUNK", 100)
    # themes
    theme_default = E("NOC_THEME_DEFAULT", "gray")
    #VC
    vc_cache_vcinterfacescount = E("NOC_VC_CACHE_VCINTERFACESCOUNT", 3600)
    vc_cache_vcprefixes = E("NOC_VC_CACHE_VCPREFIXES", 3600)

    #DNS
    dns_warn_before_expired_days = E("NOC_DNS_WARN_BEFORE_EXPIRED_DAYS", 30)

    # PMWRITER
    pm_batch_size = E("NOC_PM_BATCH_SIZE", 1000)
    pm_metrics_buffer = E("NOC_METRICS_BUFFER", pm_batch_size * 4)

    # PING
    tos = E("NOC_PING_TOS", 0)

    # syslog
    listen_syslog = E("NOC_LISTEN_SYSLOG", "0.0.0.0:514")

    def __init__(self):
        self.setup_logging()

    def use_pg_pool(self):
        self.pg_db_engine = "dbpool.db.backends.postgresql_psycopg2"
        self.pg_db_options.update({
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
            "host": self.pg_host,
            "port": self.pg_port,
            "database": self.pg_db,
            "user": self.pg_user,
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
                "db": self.mongo_db,
                "username": self.mongo_user,
                "password": self.mongo_password,
                "socketKeepAlive": True
            }
            has_credentials = self.mongo_user or self.mongo_password
            if has_credentials:
                self._mongo_connection_args["authentication_source"] = self.mongo_db
            hosts = [self.mongo_host]
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
            logging.root.setLevel(self.LOG_LEVELS[loglevel])
        else:
            # Initialize logger
            logging.basicConfig(
                stream=sys.stdout,
                format=self.log_format,
                level=self.LOG_LEVELS[loglevel]
            )
        logging.captureWarnings(True)

    def apply(self, **kwargs):
        """
        Apply additional parameters
        :param kwargs:
        :return:
        """
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def get_service(self, name):
        """
        Get service stub
        :param name:
        :return:
        """
        service = ""
        if name == "influxdb":
            service = "influxdb:8086"
        elif name == "nsqd":
            service = ["nsqd:4150"]
        elif name == "nsqlookupd":
            service = ["nsqlookupd:4161"]
        return service

# Config singleton
config = BaseConfig()
