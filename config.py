# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NOC config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import os
import socket
import sys
import urllib
from collections import namedtuple
# NOC modules
from noc.core.config.base import BaseConfig, ConfigSection
from noc.core.config.params import (
    StringParameter, MapParameter, IntParameter, BooleanParameter,
    HandlerParameter, SecondsParameter, FloatParameter,
    ServiceParameter, SecretParameter)


class Config(BaseConfig):
    loglevel = MapParameter(default="info", mappings={
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG
    })

    class activator(ConfigSection):
        tos = IntParameter(
            min=0, max=255,
            default=0
        )
        script_threads = IntParameter(default=10)
        buffer_size = IntParameter(default=1048576)
        connect_retries = IntParameter(default=3, help="retries on immediate disconnect")
        connect_timeout = IntParameter(default=3, help="timeout after immediate disconnect")
        http_connect_timeout = IntParameter(default=20)
        http_request_timeout = IntParameter(default=30)
        http_validate_cert = BooleanParameter(default=False)

    class audit(ConfigSection):
        command_ttl = SecondsParameter(default="1m")
        login_ttl = SecondsParameter(default="1m")
        reboot_ttl = SecondsParameter(default="0")
        config_ttl = SecondsParameter(default="1y")
        db_ttl = SecondsParameter(default="5y")
        config_changed_ttl = SecondsParameter(default="1y")

    class backup(ConfigSection):
        keep_days = SecondsParameter(default="14d")
        keep_weeks = SecondsParameter(default="12w")
        keep_day_of_week = IntParameter(default="6")
        keep_months = IntParameter(default="12")
        keep_day_of_month = IntParameter(default="1")

    class bi(ConfigSection):
        language = StringParameter(default="en")
        query_threads = IntParameter(default=10)
        extract_delay_alarms = SecondsParameter(default="1h")
        clean_delay_alarms = SecondsParameter(default="1d")
        reboot_interval = SecondsParameter(default="1M")
        extract_delay_reboots = SecondsParameter(default="1h")
        clean_delay_reboots = SecondsParameter(default="1d")
        chunk_size = IntParameter(default=3000)
        extract_window = SecondsParameter(default="1d")
        enable_alarms = BooleanParameter(default=False)
        enable_reboots = BooleanParameter(default=False)
        enable_managedobjects = BooleanParameter(default=False)

    brand = StringParameter(default="NOC")

    class cache(ConfigSection):
        vcinterfacescount = SecondsParameter(default="1h")
        vcprefixes = SecondsParameter(default="1h")
        cache_class = StringParameter(default="noc.core.cache.mongo.MongoCache")
        default_ttl = SecondsParameter(default="1d")
        pool_size = IntParameter(default=8)

    class card(ConfigSection):
        language = StringParameter(default="en")
        alarmheat_tooltip_limit = IntParameter(default=5)

    class chwriter(ConfigSection):
        batch_size = IntParameter(default=50000)
        records_buffer = IntParameter(default=1000000)
        batch_delay_ms = IntParameter(default=10000)
        channel_expire_interval = SecondsParameter(default="5M")
        suspend_timeout_ms = IntParameter(default=3000)
        # Topic to listen
        topic = StringParameter(default="chwriter")
        # <address:port> of ClickHouse server to write
        write_to = StringParameter()
        max_in_flight = IntParameter(default=10)

    class classifier(ConfigSection):
        lookup_handler = HandlerParameter(
            default="noc.services.classifier.rulelookup.RuleLookup")
        default_interface_profile = StringParameter(default="default")
        default_rule = StringParameter(default="Unknown | Default")

    class clickhouse(ConfigSection):
        rw_addresses = ServiceParameter(service="clickhouse", wait=True)
        db = StringParameter(default="noc")
        rw_user = StringParameter(default="default")
        rw_password = SecretParameter()
        ro_addresses = ServiceParameter(service="clickhouse", wait=True)
        ro_user = StringParameter(default="readonly")
        ro_password = SecretParameter()
        request_timeout = SecondsParameter(default="1h")
        connect_timeout = SecondsParameter(default="10s")
        default_merge_tree_granularity = IntParameter(default=8192)
        encoding = StringParameter(default="", choices=[
            "",
            "deflate",
            "gzip"
        ])
        # Cluster name for sharded/replicated configuration
        # Matches appropriative <remote_servers> part
        cluster = StringParameter()
        # Cluster topology
        # Expression in form
        # <topology> ::= <shard> | <shard>,<topology>
        # <shard> ::= [<weight>]<replicas>
        # <weight> := <DIGITS>
        # <replicas> := <DIGITS>
        # Examples:
        # 1 - non-replicated, non-sharded configuration
        # 1,1 - 2 shards, non-replicated
        # 2,2 - 2 shards, 2 replicas in each
        # 3:2,2 - first shard has 2 replicas an weight 3,
        #   second shard has 2 replicas and weight 1
        cluster_topology = StringParameter(default="1")

    class cm(ConfigSection):
        vcs_type = StringParameter(default="gridvcs", choices=["hg", "CVS", "gridvcs"])

    class consul(ConfigSection):
        token = SecretParameter()
        connect_timeout = SecondsParameter(default="5s")
        request_timeout = SecondsParameter(default="1h")
        near_retry_timeout = IntParameter(default=1)
        host = StringParameter(default="consul")
        port = IntParameter(default=8500)
        check_interval = SecondsParameter(default="10s")
        check_timeout = SecondsParameter(default="1s")
        release = SecondsParameter(default="1M")
        session_ttl = SecondsParameter(default="10s")
        lock_delay = SecondsParameter(default="20s")
        retry_timeout = SecondsParameter(default="1s")
        keepalive_attempts = IntParameter(default=5)
        base = StringParameter(default="noc", help="kv lookup base")

    class correlator(ConfigSection):
        max_threads = IntParameter(default=20)
        topology_rca_window = IntParameter(default=0)
        oo_close_delay = SecondsParameter(default="20s")
        discovery_delay = SecondsParameter(default="10M")
        auto_escalation = BooleanParameter(default=True)

    class customization(ConfigSection):
        favicon_url = StringParameter(
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
        preview_theme = StringParameter(default="midnight")

    class date_time_formats(StringParameter):
        date_format = StringParameter(default="d.m.Y")
        datetime_format = StringParameter(default="d.m.Y H:i:s")
        month_day_format = StringParameter(default="F j")
        time_format = StringParameter(default="H:i:s")
        year_month_format = StringParameter(default="F Y")

    class dcs(ConfigSection):
        resolution_timeout = SecondsParameter(default="5M")

    class discovery(ConfigSection):
        max_threads = IntParameter(default=20)
        sample = IntParameter(default=0)

    class dns(ConfigSection):
        warn_before_expired = SecondsParameter(default="30d")

    class escalator(ConfigSection):
        max_threads = IntParameter(default=5)
        retry_timeout = SecondsParameter(default="60s")
        tt_escalation_limit = IntParameter(default=10)
        ets = SecondsParameter(default="60s")
        wait_tt_check_interval = SecondsParameter(default="60s")
        sample = IntParameter(default=0)

    class features(ConfigSection):
        use_uvlib = BooleanParameter(default=False)
        cp = BooleanParameter(default=True)
        sentry = BooleanParameter(default=False)
        traefik = BooleanParameter(default=False)
        cpclient = BooleanParameter(default=False)
        telemetry = BooleanParameter(default=False, help="Enable internal telemetry export to Clickhouse")
        consul_healthchecks = BooleanParameter(default=True, help="While registering serive in consul also register health check")
        service_registration = BooleanParameter(default=True, help="Permit consul self registration")
        pypy = BooleanParameter(default=False)
        forensic = BooleanParameter(default=False)

    class fm(ConfigSection):
        active_window = SecondsParameter(default="1d")
        keep_events_wo_alarm = IntParameter(default=0)
        keep_events_with_alarm = IntParameter(default=-1)
        alarm_close_retries = IntParameter(default=5)
        outage_refresh = SecondsParameter(default="60s")
        total_outage_refresh = SecondsParameter(default="60s")

    class geocoding(ConfigSection):
        order = StringParameter(default="yandex,google")
        yandex_key = SecretParameter(default="")
        google_key = SecretParameter(default="")
        google_language = StringParameter(default="en")

    class gis(ConfigSection):
        ellipsoid = StringParameter(default="PZ-90")
        enable_osm = BooleanParameter(default=True)
        enable_google_sat = BooleanParameter(default=False)
        enable_google_roadmap = BooleanParameter(default=False)
        tile_size = IntParameter(default=256, help="Tile size 256x256")
        tilecache_padding = IntParameter(default=0)

    global_n_instances = IntParameter(default=1)

    class grafanads(ConfigSection):
        db_threads = IntParameter(default=10)

    class http_client(ConfigSection):
        connect_timeout = SecondsParameter(default="10s")
        request_timeout = SecondsParameter(default="1h")
        user_agent = StringParameter(default="noc")
        buffer_size = IntParameter(default=128 * 1024)
        max_redirects = IntParameter(default=5)

        ns_cache_size = IntParameter(default=1000)
        resolver_ttl = SecondsParameter(default="3s")

        http_port = IntParameter(default=80)
        https_port = IntParameter(default=443)
        validate_certs = BooleanParameter(default=False, help="Have to be set as True")

    class influxdb(ConfigSection):
        addresses = ServiceParameter(service="influxdb", wait=True)
        db = StringParameter(default="noc")
        user = StringParameter()
        password = SecretParameter()
        request_timeout = SecondsParameter(default="10M")
        connect_timeout = SecondsParameter(default="10s")

    installation_name = StringParameter(
        default="Unconfigured installation"
    )

    instance = IntParameter(default=0)

    language = StringParameter(default="en")
    language_code = StringParameter(
        default="en-us"
    )

    listen = StringParameter(default="auto:0")

    log_format = StringParameter(
        default="%(asctime)s [%(name)s] %(message)s"
    )

    thread_stack_size = IntParameter(default=0)

    class logging(ConfigSection):
        log_api_calls = BooleanParameter(default=False)
        log_sql_statements = BooleanParameter(default=False)

    class login(ConfigSection):
        methods = StringParameter(default="local")
        session_ttl = SecondsParameter(default="7d")
        language = StringParameter(default="en")
        restrict_to_group = StringParameter(default="")
        single_session_group = StringParameter(default="")
        mutual_exclusive_group = StringParameter(default="")
        idle_timeout = SecondsParameter(default="1w")
        pam_service = StringParameter(default="noc")
        radius_secret = SecretParameter(default="noc")
        radius_server = StringParameter()
        user_cookie_ttl = IntParameter(default=1)

    class mailsender(ConfigSection):
        smtp_server = StringParameter()
        smtp_port = IntParameter(default=25)
        use_tls = BooleanParameter(default=False)
        helo_hostname = StringParameter(default="noc")
        from_address = StringParameter(default="noc@example.com")
        smtp_user = StringParameter()
        smtp_password = SecretParameter()

    class memcached(ConfigSection):
        addresses = ServiceParameter(service="memcached", wait=True, full_result=True)
        pool_size = IntParameter(default=8)
        default_ttl = SecondsParameter(default="1d")

    class mongo(ConfigSection):
        addresses = ServiceParameter(service="mongo", wait=True)
        db = StringParameter(default="noc")
        user = StringParameter()
        password = SecretParameter()
        rs = StringParameter()
        retries = IntParameter(default=20)
        timeout = SecondsParameter(default="3s")

    class mrt(ConfigSection):
        max_concurrency = IntParameter(default=50)

    node = socket.gethostname()

    class nsqd(ConfigSection):
        addresses = ServiceParameter(service="nsqd",
                                     wait=True, near=True,
                                     full_result=False)
        http_addresses = ServiceParameter(service="nsqdhttp",
                                          wait=True, near=True,
                                          full_result=False)
        pub_retry_delay = FloatParameter(default=0.1)
        ch_chunk_size = IntParameter(default=4000)
        connect_timeout = SecondsParameter(default="3s")
        request_timeout = SecondsParameter(default="30s")
        reconnect_interval = IntParameter(default=15)
        compression = StringParameter(
            choices=["", "deflate", "snappy"],
            default=""
        )
        compression_level = IntParameter(default=6)
        max_in_flight = IntParameter(default=1)

    class nsqlookupd(ConfigSection):
        addresses = ServiceParameter(service="nsqlookupd",
                                     wait=True, near=True, full_result=False)
        http_addresses = ServiceParameter(service="nsqlookupdhttp", wait=True, full_result=False)

    class path(ConfigSection):
        smilint = StringParameter()
        smidump = StringParameter()
        dig = StringParameter()
        vcs_path = StringParameter(default="/usr/local/bin/hg")
        repo = StringParameter(default="/var/repo")
        config_mirror_path = StringParameter("")
        backup_dir = StringParameter(default="/var/backup")
        etl_import = StringParameter(default="/var/lib/noc/import")
        ssh_key_prefix = StringParameter(default="etc/noc_ssh")
        beef_prefix = StringParameter(default="/var/lib/noc/beef/sa")
        cp_new = StringParameter(default="/var/lib/noc/cp/crashinfo/new")
        bi_data_prefix = StringParameter(default="/var/lib/noc/bi")
        babel_cfg = StringParameter(default="etc/babel.cfg")
        babel = StringParameter(default="./bin/pybabel")
        pojson = StringParameter(default="./bin/pojson")
        collection_fm_mibs = StringParameter(default="collections/fm.mibs/")
        supervisor_cfg = StringParameter(default="etc/noc_services.conf")
        legacy_config = StringParameter(default="etc/noc.yml")
        cythonize = StringParameter(default="./bin/cythonize")
        npkg_root = StringParameter(default="/var/lib/noc/var/pkg")
        card_template_path = StringParameter(default="services/card/templates/card.html.j2")
        pm_templates = StringParameter(default="templates/ddash/")

    class pg(ConfigSection):
        addresses = ServiceParameter(
            service="postgres",
            wait=True, near=True, full_result=False
        )
        db = StringParameter(default="noc")
        user = StringParameter()
        password = SecretParameter()
        connect_timeout = IntParameter(default=5)

    class ping(ConfigSection):
        throttle_threshold = FloatParameter()
        restore_threshold = FloatParameter()
        tos = IntParameter(
            min=0, max=255,
            default=0
        )
        # Recommended send buffer size, 4M by default
        send_buffer = IntParameter(default=4 * 1048576)
        # Recommended receive buffer size, 4M by default
        receive_buffer = IntParameter(default=4 * 1048576)

    class pmwriter(ConfigSection):
        batch_size = IntParameter(default=2500)
        metrics_buffer = IntParameter(default=50000)
        read_from = StringParameter(default="pmwriter")
        write_to = StringParameter(default="influxdb")
        write_to_port = IntParameter(default=8086)
        max_delay = FloatParameter(default="1.0")

    class proxy(ConfigSection):
        http_proxy = StringParameter(default=os.environ.get("http_proxy"))
        https_proxy = StringParameter(default=os.environ.get("https_proxy"))
        ftp_proxy = StringParameter(default=os.environ.get("ftp_proxy"))

    pool = StringParameter(default=os.environ.get("NOC_POOL", ""))

    class rpc(ConfigSection):
        retry_timeout = StringParameter(
            default="0.1,0.5,1,3,10,30"
        )
        sync_connect_timeout = SecondsParameter(default="20s")
        sync_request_timeout = SecondsParameter(default="1h")
        sync_retry_timeout = FloatParameter(default=1.0)
        sync_retry_delta = FloatParameter(default=2.0)
        sync_retries = IntParameter(default=5)
        async_connect_timeout = SecondsParameter(default="20s")
        async_request_timeout = SecondsParameter(default="1h")

    class sae(ConfigSection):
        db_threads = IntParameter(default=20)
        activator_resolution_retries = IntParameter(default=5)
        activator_resolution_timeout = SecondsParameter(default="2s")

    class scheduler(ConfigSection):
        max_threads = IntParameter(default=20)
        submit_threshold_factor = IntParameter(default=10)
        max_chunk_factor = IntParameter(default=1)
        updates_per_check = IntParameter(default=4)
        cache_default_ttl = SecondsParameter(default="1d")
        autointervaljob_interval = SecondsParameter(default="1d")
        autointervaljob_initial_submit_interval = SecondsParameter(default="1d")

    class script(ConfigSection):
        timeout = SecondsParameter(default="2M", help="default sa script script timeout")
        session_idle_timeout = SecondsParameter(default="1M", help="defeault session timeout")
        caller_timeout = SecondsParameter(default="1M")
        calling_service = StringParameter(default="MTManager")

    secret_key = StringParameter(default="12345")

    class sentry(ConfigSection):
        url = StringParameter(default="")

    class sync(ConfigSection):
        config_ttl = SecondsParameter(default="1d")
        ttl_jitter = FloatParameter(default=0.1)
        expired_refresh_timeout = IntParameter(default=25)
        expired_refresh_chunk = IntParameter(default=100)

    class syslogcollector(ConfigSection):
        listen = StringParameter(default="0.0.0.0:514")

    class tgsender(ConfigSection):
        token = SecretParameter()
        retry_timeout = IntParameter(default=2)
        use_proxy = BooleanParameter(default=False)

    class threadpool(ConfigSection):
        idle_timeout = SecondsParameter(default="30s")
        shutdown_timeout = SecondsParameter(default="1M")

    timezone = StringParameter(
        default="Europe/Moscow"
    )

    class traceback(ConfigSection):
        reverse = BooleanParameter(default=True)

    class trapcollector(ConfigSection):
        listen = StringParameter(default="0.0.0.0:162")

    class web(ConfigSection):
        api_row_limit = IntParameter(default=0)
        api_arch_alarm_limit = IntParameter(default=4 * 86400)
        language = StringParameter(default="en")
        install_collection = BooleanParameter(default=False)
        max_threads = IntParameter(default=10)
        macdb_window = IntParameter(default=4 * 86400)

    class datasource(ConfigSection):
        chunk_size = IntParameter(default=1000)
        max_threads = IntParameter(default=10)
        default_ttl = SecondsParameter(default="1h")

    class tests(ConfigSection):
        enable_coverage = BooleanParameter(default=False)
        events_path = StringParameter(default="collections/test.events")
        profilecheck_path = StringParameter(default="collections/test.profilecheck")

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
                self._mongo_connection_args["readPreference"] = "secondaryPreferred"
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

    @property
    def ch_cluster_topology(self):
        if not hasattr(self, "_ch_cluster_topology"):
            shards = []
            for s in self.clickhouse.cluster_topology.split(","):
                s = s.strip()
                if ":" in s:
                    weight, replicas = s.split(":")
                else:
                    weight, replicas = 1, s
                shards += [CHClusterShard(int(replicas), int(weight))]
            self._ch_cluster_topology = shards
        return self._ch_cluster_topology

    def get_ch_topology_type(self):
        """
        Detect ClickHouse topology type
        :return: Any of
          * CH_UNCLUSTERED
          * CH_REPLICATED
          * CH_SHARDED
        """
        topo = self.ch_cluster_topology
        if len(topo) == 1:
            if topo[0].replicas == 1:
                return CH_UNCLUSTERED
            else:
                return CH_REPLICATED
        else:
            return CH_SHARDED


CHClusterShard = namedtuple("CHClusterShard", ["replicas", "weight"])
CH_UNCLUSTERED = 0
CH_REPLICATED = 1
CH_SHARDED = 2

config = Config()
config.load()
config.setup_logging()
