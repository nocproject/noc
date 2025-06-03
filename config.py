# ----------------------------------------------------------------------
# NOC config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import os
import socket
import sys
from functools import partial
from urllib.parse import quote as urllib_quote

# Third-party modules
import cachetools

# NOC modules
from noc.core.config.base import BaseConfig, ConfigSection
from noc.core.config.params import (
    StringParameter,
    MapParameter,
    IntParameter,
    BooleanParameter,
    HandlerParameter,
    SecondsParameter,
    BytesParameter,
    FloatParameter,
    ServiceParameter,
    SecretParameter,
    ListParameter,
    UUIDParameter,
    TimeZoneParameter,
)


class Config(BaseConfig):
    loglevel = MapParameter(
        default="info",
        mappings={
            # pylint: disable=used-before-assignment
            "critical": logging.CRITICAL,
            # pylint: disable=used-before-assignment
            "error": logging.ERROR,
            # pylint: disable=used-before-assignment
            "warning": logging.WARNING,
            # pylint: disable=used-before-assignment
            "info": logging.INFO,
            # pylint: disable=used-before-assignment
            "debug": logging.DEBUG,
        },
    )

    class activator(ConfigSection):
        tos = IntParameter(min=0, max=255, default=0)
        script_threads = IntParameter(default=10)
        buffer_size = IntParameter(default=1048576)
        connect_retries = IntParameter(default=3, help="retries on immediate disconnect")
        connect_timeout = FloatParameter(default=55.0, help="timeout after immediate disconnect")
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

    class bh(ConfigSection):
        bulk_ping_timeout = SecondsParameter(default="5s")
        bulk_ping_interval = FloatParameter(default=0.1)
        bulk_ping_max_jobs = IntParameter(default=6)
        bulk_snmp_timeout = SecondsParameter(default="10s")
        bulk_snmp_max_jobs = IntParameter(default=6)
        traceroute_tries = IntParameter(default=3)

    class bi(ConfigSection):
        language = StringParameter(default="en", help="Language BI interface")
        query_threads = IntParameter(default=10)
        extract_delay_alarms = SecondsParameter(default="1h")
        clean_delay_alarms = SecondsParameter(default="1d")
        reboot_interval = SecondsParameter(default="1M")
        alarmlogs_interval = SecondsParameter(default="1M")
        extract_delay_reboots = SecondsParameter(default="1h")
        clean_delay_reboots = SecondsParameter(default="1d")
        chunk_size = IntParameter(default=500)
        extract_window = SecondsParameter(default="1d")
        enable_alarms = BooleanParameter(default=False)
        enable_alarmlogs = BooleanParameter(default=False)
        enable_reboots = BooleanParameter(default=False)
        enable_managedobjects = BooleanParameter(default=False)
        enable_alarms_archive = BooleanParameter(default=False)
        alarms_archive_policy = MapParameter(
            default="weekly",
            mappings={
                "weekly": '{{doc["clear_timestamp"].strftime("y%Yw%W")}}',
                "monthly": '{{doc["clear_timestamp"].strftime("y%Ym%m")}}',
                "quarterly": '{{doc["clear_timestamp"].strftime("y%Y")}}'
                '_quarter{{(doc["clear_timestamp"].month-1)//3 + 1}}',
                "yearly": '{{doc["clear_timestamp"].strftime("y%Y")}}',
            },
        )
        alarms_archive_batch_limit = IntParameter(default=10000)

    class biosegmentation(ConfigSection):
        processed_trials_ttl = SecondsParameter(default="1w")

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
        metric_request_interval = SecondsParameter(default="1h")

    class chwriter(ConfigSection):
        # LiftBridge partition (CH shard id)
        shard_id = IntParameter(help="CH Shard Id", default=0)
        # Unique replica number within shard
        replica_id = IntParameter(help="CH Partition Replica Id", default=0)
        # <address:port> of ClickHouse server to write
        write_to = StringParameter()
        #
        batch_size = IntParameter(default=50000, help="Size of one portion from queue")
        batch_delay_ms = IntParameter(default=10000, help="Send every period time")

    class classifier(ConfigSection):
        ds_limit = IntParameter(default=1000)
        lookup_handler = HandlerParameter(default="noc.services.classifier.rulelookup.RuleLookup")
        default_interface_profile = StringParameter(default="default")
        default_rule = StringParameter(default="Unknown | Default")
        allowed_time_drift = SecondsParameter(default="5M")
        allowed_async_cursor = BooleanParameter(default=True, help="Use Async Processed cursor")

    class clickhouse(ConfigSection):
        rw_addresses = ServiceParameter(service="clickhouse", wait=True)
        db = StringParameter(default="noc")
        db_dictionaries = StringParameter(
            default="noc_dict", help="Database for store Dictionary Table"
        )
        rw_user = StringParameter(default="default")
        rw_password = SecretParameter()
        ro_addresses = ServiceParameter(service="clickhouse", wait=True)
        ro_user = StringParameter(default="readonly")
        ro_password = SecretParameter()
        request_timeout = SecondsParameter(default="1h")
        connect_timeout = SecondsParameter(default="10s")
        default_merge_tree_granularity = IntParameter(default=8192)
        encoding = StringParameter(default="", choices=["", "deflate", "gzip"])
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
        # Magic Number
        enable_default_value = BooleanParameter(
            default=False, help="Setting default value for Clickhouse metric Column"
        )
        # UInt
        default_UInt8 = IntParameter(default=254)
        default_UInt16 = IntParameter(default=65534)
        default_UInt32 = IntParameter(default=4294967294)
        default_UInt64 = IntParameter(default=18446744073709551614)
        # Int
        default_Int8 = IntParameter(default=-127)
        default_Int16 = IntParameter(default=-32767)
        default_Int32 = IntParameter(default=-2147483647)
        default_Int64 = IntParameter(default=-9223372036854775807)
        # Float
        default_Float32 = FloatParameter(default=-2147483647.0)
        default_Float64 = FloatParameter(default=-9223372036854775807.0)

    class collections(ConfigSection):
        allow_sharing = BooleanParameter(default=True)
        allow_overwrite = BooleanParameter(default=True)

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
        topology_rca_window = SecondsParameter(default=0)
        discovery_delay = SecondsParameter(default="10M")
        auto_escalation = BooleanParameter(default=True)
        rca_lock_initial_timeout = FloatParameter(default=0.1)
        rca_lock_max_timeout = FloatParameter(default=3.0)
        rca_lock_rate = FloatParameter(default=1.61)
        rca_lock_dev = FloatParameter(default=0.1)
        rca_lock_expiry = SecondsParameter(default="10s")
        allowed_async_cursor = BooleanParameter(default=False)
        object_status_update_interval = SecondsParameter(default="2s")

    class customization(ConfigSection):
        favicon_url = StringParameter(default="/ui/web/img/logo_24x24_deep_azure.png")
        logo_url = StringParameter(default="/ui/web/img/logo_white.svg")
        logo_width = IntParameter(default=24)
        logo_height = IntParameter(default=24)
        branding_color = StringParameter(default="#ffffff")
        branding_background_color = StringParameter(default="#34495e")
        preview_theme = StringParameter(default="midnight")

    class date_time_formats(StringParameter):
        date_format = StringParameter(default="d.m.Y")
        datetime_format = StringParameter(default="d.m.Y H:i:s")
        month_day_format = StringParameter(default="F j")
        time_format = StringParameter(default="H:i:s")
        year_month_format = StringParameter(default="F Y")

    class dcs(ConfigSection):
        resolution_timeout = SecondsParameter(default="5M")
        resolver_expiration_timeout = SecondsParameter(default="10M")

    class discovery(ConfigSection):
        max_threads = IntParameter(default=20)
        proxy_metric = BooleanParameter(
            default=False, help="Send metrics discovery result from self"
        )
        sync_diagnostic_labels = BooleanParameter(
            default=True, help="Sync diagnostic labels on Box discovery"
        )
        sample = IntParameter(default=0)
        min_metric_interval = IntParameter(default=60)
        job_check_interval = IntParameter(default=1000, min=1000)
        interface_metric_service = BooleanParameter(
            default=True,
            help="Add service field to metric request",
        )

    class dns(ConfigSection):
        warn_before_expired = SecondsParameter(default="30d")

    class escalator(ConfigSection):
        max_threads = IntParameter(default=5)
        retry_timeout = SecondsParameter(default="60s")
        tt_escalation_limit = IntParameter(default=10)
        ets = SecondsParameter(default="60s")
        wait_tt_check_interval = SecondsParameter(default="60s")
        sample = IntParameter(default=0)
        job_check_interval = IntParameter(default=5000, min=1000)

    class etl(ConfigSection):
        compression = StringParameter(choices=["plain", "gzip", "bz2", "lzma"], default="gzip")

    class features(ConfigSection):
        use_uvloop = BooleanParameter(default=False)
        cp = BooleanParameter(default=True)
        sentry = BooleanParameter(default=False)
        traefik = BooleanParameter(default=False)
        cpclient = BooleanParameter(default=False)
        telemetry = BooleanParameter(
            default=False, help="Enable internal telemetry export to Clickhouse"
        )
        consul_healthchecks = BooleanParameter(
            default=True, help="While registering serive in consul also register health check"
        )
        service_registration = BooleanParameter(
            default=True, help="Permit consul self registration"
        )
        forensic = BooleanParameter(default=False)
        gate = ListParameter(item=StringParameter(), default=[], help="Feature gates")

    class fm(ConfigSection):
        active_window = SecondsParameter(default="1d")
        keep_events_wo_alarm = IntParameter(default=0)
        keep_events_with_alarm = IntParameter(default=-1)
        alarm_close_retries = IntParameter(default=5)
        outage_refresh = SecondsParameter(default="60s")
        total_outage_refresh = SecondsParameter(default="60s")
        generate_message_id = BooleanParameter(
            default=False, help="Generate UUID for received Syslog and SNMP message"
        )

    class geocoding(ConfigSection):
        order = StringParameter(default="yandex,google")
        yandex_apikey = SecretParameter(default="")
        google_key = SecretParameter(default="")
        google_language = StringParameter(default="en")
        negative_ttl = SecondsParameter(default="7d", help="Period then saving bad result")
        ui_geocoder = StringParameter(default="")

    class gis(ConfigSection):
        ellipsoid = StringParameter(default="PZ-90")
        enable_blank = BooleanParameter(default=False)
        enable_osm = BooleanParameter(default=True)
        enable_google_roadmap = BooleanParameter(default=False)
        enable_google_hybrid = BooleanParameter(default=False)
        enable_google_sat = BooleanParameter(default=False)
        enable_google_terrain = BooleanParameter(default=False)
        enable_tile1 = BooleanParameter(default=False)
        tile1_name = StringParameter(default="Custom 1")
        tile1_url = StringParameter(default="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
        tile1_subdomains = ListParameter(item=StringParameter(), default=[])
        enable_tile2 = BooleanParameter(default=False)
        tile2_name = StringParameter(default="Custom 2")
        tile2_url = StringParameter(default="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
        tile2_subdomains = ListParameter(item=StringParameter(), default=[])
        enable_tile3 = BooleanParameter(default=False)
        tile3_name = StringParameter(default="Custom 3")
        tile3_url = StringParameter(default="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
        tile3_subdomains = ListParameter(item=StringParameter(), default=[])
        yandex_supported = BooleanParameter(default=False)
        enable_yandex_roadmap = BooleanParameter(default=False)
        enable_yandex_hybrid = BooleanParameter(default=False)
        enable_yandex_sat = BooleanParameter(default=False)
        default_layer = StringParameter(default="osm")
        tile_size = IntParameter(default=256, help="Tile size 256x256")

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

    class initial(ConfigSection):
        admin_user_name = StringParameter(default="admin")
        admin_password = StringParameter(default="admin")
        admin_email = StringParameter(default="test@example.com")

    installation_name = StringParameter(default="Unconfigured installation")
    installation_id = UUIDParameter(default="")

    instance = IntParameter(default=0)

    class kafkasender(ConfigSection):
        bootstrap_servers = StringParameter()
        username = StringParameter()
        password = SecretParameter()
        sasl_mechanism = StringParameter(
            choices=["PLAIN", "GSSAPI", "SCRAM-SHA-256", "SCRAM-SHA-512"], default="PLAIN"
        )
        security_protocol = StringParameter(
            choices=["PLAINTEXT", "SASL_PLAINTEXT", "SSL", "SASL_SSL"], default="PLAINTEXT"
        )
        max_batch_size = BytesParameter(
            default=16384, help="Maximum size of buffered data per partition"
        )
        max_request_size = BytesParameter(default=1048576, help="The maximum size of a request")
        compression_type = StringParameter(
            default="none",
            choices=["none", "gzip", "snappy", "lz4", "zstd"],
            help="The compression type for all data generated by the producer",
        )

    language = StringParameter(default="en")
    language_code = StringParameter(default="en")

    class layout(ConfigSection):
        ring_ring_edge = IntParameter(default=150)
        ring_chain_edge = IntParameter(default=150)
        ring_chain_spacing = IntParameter(default=100)
        tree_horizontal_step = IntParameter(default=100)
        tree_vertical_step = IntParameter(default=100)
        tree_max_levels = IntParameter(default=4)
        spring_propulsion_force = FloatParameter(default=1.5)
        spring_edge_force = FloatParameter(default=1.2)
        spring_bubble_force = FloatParameter(default=2.0)
        spring_edge_spacing = IntParameter(default=190)
        spring_iterations = IntParameter(default=50)

    class liftbridge(ConfigSection):
        addresses = ServiceParameter(service="liftbridge", wait=True, near=True, full_result=False)
        publish_async_ack_timeout = IntParameter(default=10)
        compression_threshold = IntParameter(default=524288)
        compression_method = StringParameter(choices=["", "zlib", "lzma"], default="zlib")
        enable_http_proxy = BooleanParameter(default=False)

    listen = StringParameter(default="auto:0")

    log_format = StringParameter(default="%(asctime)s [%(name)s] %(message)s")

    thread_stack_size = IntParameter(default=0)
    version_format = StringParameter(default="%(version)s+%(branch)s.%(number)s.%(changeset)s")

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
        register_last_login = BooleanParameter(default=True)
        max_inactivity = IntParameter(default=0)
        jwt_cookie_name = StringParameter(default="noc_jwt")
        jwt_algorithm = StringParameter(default="HS256", choices=["HS256", "HS384", "HS512"])
        min_password_len = IntParameter(default=0)
        min_password_uppercase = IntParameter(default=0)
        min_password_lowercase = IntParameter(default=0)
        min_password_numbers = IntParameter(default=0)
        min_password_specials = IntParameter(default=0)
        password_ttl = SecondsParameter(default="0")
        password_history = IntParameter(default=0)

    class mailsender(ConfigSection):
        smtp_server = StringParameter()
        smtp_port = IntParameter(default=25)
        use_tls = BooleanParameter(default=False)
        helo_hostname = StringParameter(default="noc")
        from_address = StringParameter(default="noc@example.com")
        smtp_user = StringParameter()
        smtp_password = SecretParameter()

    class metricscollector(ConfigSection):
        ds_limit = IntParameter(default=1000)

    class memcached(ConfigSection):
        addresses = ServiceParameter(service="memcached", wait=True, full_result=True)
        pool_size = IntParameter(default=8)
        default_ttl = SecondsParameter(default="1d")

    class message(ConfigSection):
        enable_alarm = BooleanParameter(default=False)
        enable_event = BooleanParameter(default=False)
        enable_managedobject = BooleanParameter(default=False)
        enable_reboot = BooleanParameter(default=False)
        enable_metrics = BooleanParameter(default=False)
        # Comma-separated list of metric scopes
        enable_metric_scopes = ListParameter(item=StringParameter(), default=[])
        #
        enable_snmptrap = BooleanParameter(default=False)
        enable_syslog = BooleanParameter(default=False)
        #
        enable_diagnostic_change = BooleanParameter(default=False)
        #
        embedded_router = BooleanParameter(
            default=True, help="Use embedded process router for sending message"
        )
        #
        ds_limit = IntParameter(default=1000)

    class mongo(ConfigSection):
        addresses = ServiceParameter(service="mongo", wait=True)
        db = StringParameter(default="noc")
        user = StringParameter()
        password = SecretParameter()
        rs = StringParameter()
        retries = IntParameter(default=20)
        timeout = SecondsParameter(default="3s")
        retry_writes = BooleanParameter(default=False)
        app_name = StringParameter()
        max_idle_time = SecondsParameter(default="60s")

    class mrt(ConfigSection):
        max_concurrency = IntParameter(default=50)
        enable_command_logging = BooleanParameter(default=False)

    node = socket.gethostname()

    class nbi(ConfigSection):
        max_threads = IntParameter(default=10)
        objectmetrics_max_interval = SecondsParameter(default="3h")

    class network_scan(ConfigSection):
        purgatorium_ttl = SecondsParameter(default="4w")

    class path(ConfigSection):
        smilint = StringParameter()
        smidump = StringParameter()
        dig = StringParameter()
        vcs_path = StringParameter(default="/usr/local/bin/hg")
        repo = StringParameter(default="/var/repo")
        backup_dir = StringParameter(default="/var/backup")
        etl_import = StringParameter(default="/var/lib/noc/import")
        ssh_key_prefix = StringParameter(default="etc/noc_ssh")
        cp_new = StringParameter(default="/var/lib/noc/cp/crashinfo/new")
        bi_data_prefix = StringParameter(default="/var/lib/noc/bi")
        collection_fm_mibs = StringParameter(default="collections/fm.mibs/")
        supervisor_cfg = StringParameter(default="etc/noc_services.conf")
        legacy_config = StringParameter(default="etc/noc.yml")
        npkg_root = StringParameter(default="/var/lib/noc/var/pkg")
        card_template_path = StringParameter(default="services/card/templates/card.html.j2")
        pm_templates = StringParameter(default="templates/ddash/")
        custom_path = StringParameter()
        mib_path = StringParameter(default="/var/lib/noc/mibs/")
        cdn_url = StringParameter()
        mac_vendor_url = StringParameter(default="https://standards-oui.ieee.org/oui/oui.txt")
        mac_vendor_medium_url = StringParameter(
            default="https://standards-oui.ieee.org/oui28/mam.txt"
        )

    class pg(ConfigSection):
        addresses = ServiceParameter(service="postgres", wait=True, near=True, full_result=False)
        db = StringParameter(default="noc")
        user = StringParameter()
        password = SecretParameter()
        connect_timeout = IntParameter(default=5)

    class ping(ConfigSection):
        throttle_threshold = FloatParameter()
        restore_threshold = FloatParameter()
        tos = IntParameter(min=0, max=255, default=0)
        # Recommended send buffer size, 4M by default
        send_buffer = IntParameter(default=4 * 1048576)
        # Recommended receive buffer size, 4M by default
        receive_buffer = IntParameter(default=4 * 1048576)
        # DataStream request limit
        ds_limit = IntParameter(default=1000)

    class proxy(ConfigSection):
        http_proxy = StringParameter(default=os.environ.get("http_proxy"))
        https_proxy = StringParameter(default=os.environ.get("https_proxy"))
        ftp_proxy = StringParameter(default=os.environ.get("ftp_proxy"))

    pool = StringParameter(default=os.environ.get("NOC_POOL", ""))

    class redis(ConfigSection):
        addresses = ServiceParameter(service="redis", wait=True, full_result=True)
        db = IntParameter(default=0)
        default_ttl = SecondsParameter(default="1d")

    class redpanda(ConfigSection):
        addresses = ServiceParameter(service="redpanda", wait=False, near=True, full_result=False)
        bootstrap_servers = StringParameter()
        username = StringParameter()
        password = SecretParameter()
        sasl_mechanism = StringParameter(
            choices=["PLAIN", "GSSAPI", "SCRAM-SHA-256", "SCRAM-SHA-512"], default="PLAIN"
        )
        security_protocol = StringParameter(
            choices=["PLAINTEXT", "SASL_PLAINTEXT", "SSL", "SASL_SSL"], default="PLAINTEXT"
        )
        max_batch_size = BytesParameter(
            default=16384, help="Maximum size of buffered data per partition"
        )
        retry_backoff_ms = SecondsParameter(
            default=3,
            help="The amount of time to wait before attempting to retry a failed request to a given topic partition",
        )
        max_request_size = BytesParameter(default=1048576, help="The maximum size of a request")
        compression_type = StringParameter(
            default="lz4",
            choices=["none", "gzip", "snappy", "lz4", "zstd"],
            help="The compression type for all data generated by the producer",
        )

    class rpc(ConfigSection):
        retry_timeout = StringParameter(default="0.1,0.5,1,3,10,30")
        sync_connect_timeout = SecondsParameter(default="20s")
        sync_request_timeout = SecondsParameter(default="1h")
        sync_retry_timeout = FloatParameter(default=1.0)
        sync_retry_delta = FloatParameter(default=2.0)
        sync_retries = IntParameter(default=5)
        async_connect_timeout = SecondsParameter(default="20s")
        async_request_timeout = SecondsParameter(default="1h")

    class runner(ConfigSection):
        max_running = IntParameter(default=10)

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
        session_idle_timeout = SecondsParameter(default="1M", help="default session timeout")
        caller_timeout = SecondsParameter(default="1M")
        calling_service = StringParameter(default="script")

    secret_key = StringParameter(default="12345")

    class selfmon(ConfigSection):
        enable_managedobject = BooleanParameter(default=True)
        managedobject_ttl = IntParameter(default=30)
        enable_task = BooleanParameter(default=False)
        task_ttl = IntParameter(default=30)
        enable_inventory = BooleanParameter(default=False)
        inventory_ttl = IntParameter(default=30)
        enable_fm = BooleanParameter(default=False)
        fm_ttl = IntParameter(default=30)
        enable_liftbridge = BooleanParameter(default=False)
        liftbridge_ttl = IntParameter(default=30)

    class sentry(ConfigSection):
        url = StringParameter(default="")
        shutdown_timeout = IntParameter(min=1, max=10, default=2)
        default_integrations = BooleanParameter(default=False)
        debug = BooleanParameter(default=False)
        max_breadcrumbs = IntParameter(min=1, max=100, default=10)

    class topo(ConfigSection):
        ds_limit = IntParameter(default=1000)
        dry_run = BooleanParameter(default=False)
        check = BooleanParameter(default=True)
        interval = SecondsParameter(default=60)
        enable_scheduler_task = BooleanParameter(default=True)

    class msgstream(ConfigSection):
        metrics_send_delay = FloatParameter(default=0.25)
        max_message_size = IntParameter(default=921600, help="Max message size for GRPC client")
        client_class = StringParameter(default="noc.core.msgstream.liftbridge.LiftBridgeClient")

        class events(ConfigSection):
            retention_max_age = SecondsParameter(
                default="24h",
                help="FM events stream retention interval. If 0 use Liftbrdige setting value",
            )
            retention_max_bytes = BytesParameter(
                default=0,
                help="FM events stream retention size (in bytes). If 0 use Liftbrdige setting value",
            )
            segment_max_age = SecondsParameter(
                default="1h",
                help="FM events stream segment interval. Must be less retention age. If 0 use Liftbrdige setting value",
            )
            segment_max_bytes = BytesParameter(
                default=0,
                help="FM events stream segment size. Must be less retention size. If 0 use Liftbrdige setting value",
            )
            auto_pause_time = SecondsParameter(
                default=0, help="FM events stream pause time. If 0 use Liftbrdige setting value"
            )
            auto_pause_disable_if_subscribers = BooleanParameter(default=False)

        class dispose(ConfigSection):
            retention_max_age = SecondsParameter(
                default="24h",
                help="FM alarms stream retention interval. If 0 use Liftbrdige setting value",
            )
            retention_max_bytes = BytesParameter(
                default=0,
                help="FM alarms stream retention size (in bytes). If 0 use Liftbrdige setting value",
            )
            segment_max_age = SecondsParameter(
                default="1h",
                help="FM alarms stream segment interval. Must be less retention age. If 0 use Liftbrdige setting value",
            )
            segment_max_bytes = BytesParameter(
                default=0,
                help="FM alarms stream segment size. Must be less retention size. If 0 use Liftbrdige setting value",
            )
            auto_pause_time = SecondsParameter(
                default=0, help="FM alarms stream pause time. If 0 use Liftbrdige setting value"
            )
            auto_pause_disable_if_subscribers = BooleanParameter(default=False)

        class message(ConfigSection):
            retention_max_age = SecondsParameter(default="1h")
            retention_max_bytes = BytesParameter(default=0)
            segment_max_age = SecondsParameter(default="30M")
            segment_max_bytes = BytesParameter(default=0)
            auto_pause_time = SecondsParameter(default=0)
            auto_pause_disable_if_subscribers = BooleanParameter(default=False)

        class ch(ConfigSection):
            retention_max_age = SecondsParameter(default="1h")
            retention_max_bytes = BytesParameter(default="100M")
            segment_max_age = SecondsParameter(default="30M")
            segment_max_bytes = BytesParameter(default="50M")
            auto_pause_time = SecondsParameter(default=0)
            auto_pause_disable_if_subscribers = BooleanParameter(default=False)
            replication_factor = IntParameter(
                default=1, help="Replicaton factor for clickhouse streams"
            )

        class kafkasender(ConfigSection):
            retention_max_age = SecondsParameter(default="1h")
            retention_max_bytes = BytesParameter(default=0)
            segment_max_age = SecondsParameter(default="30M")
            segment_max_bytes = BytesParameter(default=0)
            auto_pause_time = SecondsParameter(default=0)
            auto_pause_disable_if_subscribers = BooleanParameter(default=False)

        class metrics(ConfigSection):
            retention_max_age = SecondsParameter(default="1h")
            retention_max_bytes = BytesParameter(default=0)
            segment_max_age = SecondsParameter(default="30M")
            segment_max_bytes = BytesParameter(default=0)
            auto_pause_time = SecondsParameter(default=0)
            auto_pause_disable_if_subscribers = BooleanParameter(default=False)

        class jobs(ConfigSection):
            retention_max_age = SecondsParameter(default="24h")
            retention_max_bytes = BytesParameter(default=0)
            segment_max_age = SecondsParameter(default="1h")
            segment_max_bytes = BytesParameter(default=0)
            auto_pause_time = SecondsParameter(default=0)

        class submit(ConfigSection):
            retention_max_age = SecondsParameter(default="24h")
            retention_max_bytes = BytesParameter(default=0)
            segment_max_age = SecondsParameter(default="1h")
            segment_max_bytes = BytesParameter(default=0)
            auto_pause_time = SecondsParameter(default=0)

    class syslogcollector(ConfigSection):
        listen = StringParameter(default="0.0.0.0:514")
        enable_reuseport = BooleanParameter(default=True)
        enable_freebind = BooleanParameter(default=False)
        # DataStream request limit
        ds_limit = IntParameter(default=1000)

    class tgsender(ConfigSection):
        token = SecretParameter()
        retry_timeout = IntParameter(default=2)
        use_proxy = BooleanParameter(default=False)
        proxy_address = StringParameter()

    class threadpool(ConfigSection):
        idle_timeout = SecondsParameter(default="30s")
        shutdown_timeout = SecondsParameter(default="1M")

    timezone = TimeZoneParameter(default="Europe/Moscow")

    class traceback(ConfigSection):
        reverse = BooleanParameter(default=True)

    class trapcollector(ConfigSection):
        listen = StringParameter(default="0.0.0.0:162")
        enable_reuseport = BooleanParameter(default=True)
        enable_freebind = BooleanParameter(default=False)
        # DataStream request limit
        ds_limit = IntParameter(default=1000)
        # storm protection round duration in seconds
        storm_round_duration = SecondsParameter(default="60s")
        # conversion rate between ON and OFF storm protection thresholds
        storm_threshold_reduction = FloatParameter(default=0.9)
        # time to live (rounds quantity) of records in storm protection addresses dictionary
        storm_record_ttl = IntParameter(default=10)

    class watchdog(ConfigSection):
        enable_watchdog = BooleanParameter(default=True)
        check_interval = IntParameter(default=30, help="Run interval")
        failed_count = IntParameter(default=6, help="Failed check for force reboot")

    class web(ConfigSection):
        theme = StringParameter(default="gray")
        api_row_limit = IntParameter(default=0)
        api_unlimited_row_limit = IntParameter(default=1000)
        api_arch_alarm_limit = IntParameter(default=4 * 86400)
        api_alarm_comments_limit = IntParameter(
            default=10, help="Max Alarm comment count on UI Popup"
        )
        max_upload_size = IntParameter(default=16777216)
        language = StringParameter(default="en")
        install_collection = BooleanParameter(default=False)
        max_threads = IntParameter(default=10)
        macdb_window = IntParameter(default=4 * 86400)
        enable_remote_system_last_extract_info = BooleanParameter(default=False)
        heatmap_lon = StringParameter(default="108.567849")
        heatmap_lat = StringParameter(default="66.050063")
        heatmap_zoom = StringParameter(default="4")
        map_lon = StringParameter(default="108.567849")
        map_lat = StringParameter(default="66.050063")
        max_image_size = BytesParameter(default="2M")
        topology_map_grid_size = IntParameter(min=5, default=25)
        report_csv_delimiter = StringParameter(choices=[";", ","], default=";")
        enable_report_history = BooleanParameter(
            default=False, help="Enable Save Report Execution history"
        )

    class ui(ConfigSection):
        max_avatar_size = BytesParameter(default="256K")
        max_rest_limit = IntParameter(default=100)

    class datasource(ConfigSection):
        chunk_size = IntParameter(default=1000)
        max_threads = IntParameter(default=10)
        default_ttl = SecondsParameter(default="1h")

    class datastream(ConfigSection):
        max_await_time = SecondsParameter(
            default=30,
            help="The maximum time in seconds for the server to wait for changes before responding to a getMore operation",
        )
        enable_administrativedomain = BooleanParameter(default=False)
        enable_administrativedomain_wait = BooleanParameter(
            default=True,
            help="Activate Wait Mode for Adm. Domain datastream (Mongo greater 3.6 needed)",
        )
        administrativedomain_ttl = SecondsParameter(
            default="0",
            help="Removing datastream administrativedomain records older days",
        )
        enable_alarm = BooleanParameter(default=False)
        enable_alarm_wait = BooleanParameter(
            default=True, help="Activate Wait Mode for Alarm datastream (Mongo greater 3.6 needed)"
        )
        alarm_ttl = SecondsParameter(
            default="14d",
            help="Removing datastream alarm records older days",
        )
        enable_cfgmetrics = BooleanParameter(default=True)
        enable_cfgmetrics_wait = BooleanParameter(
            default=True,
            help="Activate Wait Mode for CfgMetricsCollector datastream (Mongo greater 3.6 needed)",
        )
        cfgmetrics_ttl = SecondsParameter(
            default="0",
            help="Removing datastream cfgmetricscollector records older days",
        )
        enable_cfgmxroute = BooleanParameter(default=True)
        enable_cfgmxroute_wait = BooleanParameter(
            default=True,
            help="Activate Wait Mode for CfgMXRoute datastream (Mongo greater 3.6 needed)",
        )
        cfgmxroute_ttl = SecondsParameter(
            default="0",
            help="Removing datastream CfgMXRoute records older days",
        )
        enable_cfgmetricrules = BooleanParameter(default=True)
        enable_cfgmetricrules_wait = BooleanParameter(
            default=True,
            help="Activate Wait Mode for CfgMetricRules datastream (Mongo greater 3.6 needed)",
        )
        cfgmetricrules_ttl = SecondsParameter(
            default="0",
            help="Removing datastream CfgMetricRules records older days",
        )
        enable_cfgmetricsources = BooleanParameter(default=True)
        enable_cfgmetricsources_wait = BooleanParameter(
            default=True,
            help="Activate Wait Mode for CfgMOMappingCollector datastream (Mongo greater 3.6 needed)",
        )
        cfgmetricsources_ttl = SecondsParameter(
            default="0",
            help="Removing datastream CfgMOMappingcollector records older days",
        )
        enable_cfgtarget = BooleanParameter(default=True)
        enable_cfgtarget_wait = BooleanParameter(default=True)
        cfgtarget_ttl = SecondsParameter(
            default="0",
            help="Removing datastream cfgtarget records older days",
        )
        enable_cfgeventrules = BooleanParameter(default=True)
        enable_cfgeventrules_wait = BooleanParameter(default=True)
        cfgeventrules_ttl = SecondsParameter(
            default="0",
            help="Removing datastream cfgtarget records older days",
        )
        enable_cfgevent = BooleanParameter(default=True)
        enable_cfgevent_wait = BooleanParameter(default=True)
        cfgevent_ttl = SecondsParameter(
            default="0",
            help="Removing datastream cfgtarget records older days",
        )
        enable_dnszone = BooleanParameter(default=False)
        enable_dnszone_wait = BooleanParameter(
            default=True,
            help="Activate Wait Mode for DNS Zone datastream (Mongo greater 3.6 needed)",
        )
        dnszone_ttl = SecondsParameter(
            default="0",
            help="Removing datastream dnszone records older days",
        )
        enable_managedobject = BooleanParameter(default=False)
        enable_managedobject_wait = BooleanParameter(
            default=True,
            help="Activate Wait Mode for ManagedObject datastream (Mongo greater 3.6 needed)",
        )
        managedobject_ttl = SecondsParameter(
            default="0",
            help="Removing datastream managedobject records older days",
        )
        enable_resourcegroup = BooleanParameter(default=False)
        enable_resourcegroup_wait = BooleanParameter(
            default=True,
            help="Activate Wait Mode for ResourceGroup datastream (Mongo greater 3.6 needed)",
        )
        resourcegroup_ttl = SecondsParameter(
            default="0",
            help="Removing datastream resourcegroup records older days",
        )
        enable_vrf = BooleanParameter(default=False)
        enable_vrf_wait = BooleanParameter(
            default=True, help="Activate Wait Mode for VRF datastream (Mongo greater 3.6 needed)"
        )
        vrf_ttl = SecondsParameter(
            default="0",
            help="Removing datastream vrf records older days",
        )
        enable_prefix = BooleanParameter(default=False)
        enable_prefix_wait = BooleanParameter(
            default=True, help="Activate Wait Mode for Prefix datastream (Mongo greater 3.6 needed)"
        )
        prefix_ttl = SecondsParameter(
            default="0",
            help="Removing datastream prefix records older days",
        )
        enable_address = BooleanParameter(default=False)
        enable_address_wait = BooleanParameter(
            default=True,
            help="Activate Wait Mode for Address datastream (Mongo greater 3.6 needed)",
        )
        address_ttl = SecondsParameter(
            default="0",
            help="Removing datastream address records older days",
        )
        enable_service = BooleanParameter(default=False)
        enable_service_wait = BooleanParameter(
            default=True,
            help="Activate Wait Mode for Service datastream (Mongo greater 3.6 needed)",
        )
        service_ttl = SecondsParameter(
            default="0",
            help="Removing datastream service records older days",
        )

    class help(ConfigSection):
        base_url = StringParameter(default="https://docs.getnoc.com")
        branch = StringParameter(default="microservices")
        language = StringParameter(default="en")

    class tests(ConfigSection):
        # List of pyfilesystem URLs holding intial data
        fixtures_paths = ListParameter(item=StringParameter(), default=["tests/data"])
        # List of pyfilesystem URLs holding event classification samples
        events_paths = ListParameter(item=StringParameter())
        # List of pyfilesystem URLs holding beef test cases
        beef_paths = ListParameter(item=StringParameter())

    class peer(ConfigSection):
        enable_ripe = BooleanParameter(default=True)
        enable_arin = BooleanParameter(default=True)
        enable_radb = BooleanParameter(default=True)
        prefix_list_optimization = BooleanParameter(default=True)
        prefix_list_optimization_threshold = IntParameter(default=1000)
        max_prefix_length = IntParameter(default=24)
        rpsl_inverse_pref_style = BooleanParameter(default=False)

    class perfomance(ConfigSection):
        default_hist = ListParameter(
            item=FloatParameter(), default=[0.001, 0.005, 0.01, 0.05, 0.5, 1.0, 5.0, 10.0]
        )
        enable_mongo_hist = BooleanParameter(default=False)
        mongo_hist = ListParameter(
            item=FloatParameter(), default=[0.001, 0.005, 0.01, 0.05, 0.5, 1.0, 5.0, 10.0]
        )
        enable_postgres_hist = BooleanParameter(default=False)
        postgres_hist = ListParameter(
            item=FloatParameter(), default=[0.001, 0.005, 0.01, 0.05, 0.5, 1.0, 5.0, 10.0]
        )
        default_quantiles = ListParameter(item=FloatParameter(), default=[0.5, 0.9, 0.95])
        default_quantiles_epsilon = 0.01
        default_quantiles_window = 60
        default_quantiles_buffer = 100
        enable_mongo_quantiles = BooleanParameter(default=False)
        enable_postgres_quantiles = BooleanParameter(default=False)

    class metrics(ConfigSection):
        # Disable On Start, that compact procedure lost Consul session
        compact_on_start = BooleanParameter(default=False)
        compact_on_stop = BooleanParameter(default=False)
        flush_interval = SecondsParameter(default="1M")
        compact_interval = SecondsParameter(default="5M")
        # Metrics
        disable_spool = BooleanParameter(default=False, help="Disable send metrics to Clickhouse")
        # DCS Client
        check_interval = SecondsParameter(default="20s")
        check_timeout = SecondsParameter(default="15s")
        # DataStream request limit
        ds_limit = IntParameter(default=1000)

    # pylint: disable=super-init-not-called
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
            "password": self.pg.password,
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
            }
            if self.mongo.app_name:
                self._mongo_connection_args["appname"] = self.mongo.app_name
            if self.mongo.retry_writes:
                self._mongo_connection_args["retryWrites"] = True
            has_credentials = self.mongo.user or self.mongo.password
            if has_credentials:
                self._mongo_connection_args["authentication_source"] = self.mongo.db
            hosts = self.mongo.addresses
            if self.mongo.rs:
                self._mongo_connection_args["replicaSet"] = self.mongo.rs
                self._mongo_connection_args["readPreference"] = "secondaryPreferred"
            elif len(hosts) > 1:
                raise ValueError("Replica set name must be set")
            if self.mongo.max_idle_time:
                self._mongo_connection_args["maxIdleTimeMS"] = self.mongo.max_idle_time * 1000
            url = ["mongodb://"]
            if has_credentials:
                url += [
                    "%s:%s@" % (urllib_quote(self.mongo.user), urllib_quote(self.mongo.password))
                ]
            url += [",".join(str(h) for h in hosts)]
            url += ["/%s" % self.mongo.db]
            self._mongo_connection_args["host"] = "".join(url)
            if self.perfomance.enable_mongo_hist:
                from noc.core.mongo.monitor import MongoCommandSpan

                self._mongo_connection_args["event_listeners"] = [MongoCommandSpan()]
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
            logging.basicConfig(stream=sys.stdout, format=self.log_format, level=loglevel)
        logging.captureWarnings(True)

    def get_customized_paths(self, *args, **kwargs):
        """
        Check for customized path for given repo path.
        Repo path may be given in os.path.join-style components.
        Returns list of possible paths. One of elements is always repo path,
        while other may be custom counterpart, if exists.
        :param prefer_custom: True - customized path first, False - repo path first
        :param args: Path or path components in os.path.join-style
        :return: List of possible paths
        """
        prefer_custom = kwargs.get("prefer_custom", False)
        rpath = os.path.join(*args)
        if not self.path.custom_path:
            return [rpath]
        cpath = os.path.join(self.path.custom_path, *args)
        if os.path.exists(cpath):
            if prefer_custom:
                return [cpath, rpath]
            else:
                return [rpath, cpath]
        return [rpath]

    def get_hist_config(self, name):
        """
        Get configuration for hist `name`. Returns list of times or None, if hist is disabled
        :param name: Hist name
        :return: List of hist config or None
        """
        # Check hist is enabled
        if not getattr(self.perfomance, f"enable_{name}_hist", False):
            return None
        # Get config
        cfg = getattr(self.perfomance, f"{name}_hist")
        if cfg:
            return cfg
        # Fallback to defaults
        return self.perfomance.default_hist or None

    def get_quantiles_config(self, name):
        """
        Check if quantile is enabled
        :return: True if quantile is enabled
        """
        # Check quantiles is enabled
        return getattr(self.perfomance, f"enable_{name}_quantiles", False)

    @property
    def tz_utc_offset(self) -> int:
        """
        Return UTC offset for configured timezone
        :return:
        """
        import pytz
        import datetime

        if not hasattr(self, "_utcoffset"):
            dt = datetime.datetime.now(tz=pytz.utc)
            self._utcoffset = dt.astimezone(self.timezone).utcoffset()
        return int(self._utcoffset.total_seconds())

    @staticmethod
    @cachetools.cached(cachetools.TTLCache(maxsize=128, ttl=60))
    def get_slot_limits(slot_name):
        """
        Get slot count
        :param slot_name:
        :return:
        """
        from noc.core.dcs.loader import get_dcs
        from noc.core.ioloop.util import run_sync

        dcs = get_dcs()
        return run_sync(partial(dcs.get_slot_limit, slot_name))


config = Config()
config.load()
config.setup_logging()
