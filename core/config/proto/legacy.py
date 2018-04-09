# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Load legacy noc.yml
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import logging
# Third-party modules
import yaml
# NOC modules
from .base import BaseProtocol

logger = logging.getLogger(__name__)


class LegacyProtocol(BaseProtocol):
    """
    Load legacy noc.yml file
    Usage:

    legacy:///
    """
    NOC_MAPPINGS = [
        ("noc.installation_name", "installation_name"),
        ("noc.language", "language"),
        ("noc.mongo_password", "mongo.password"),
        ("noc.mongo_user", "mongo.user"),
        ("noc.mongo_rs", "mongo.rs"),
        ("noc.mongo_db", "mongo.db"),
        ("noc.pg_db", "pg.db"),
        ("noc.pg_password", "pg.password"),
        ("noc.pg_user", "pg.user"),
        ("noc.influx_db", "influxdb.db"),
        ("noc.influx_password", "influxdb.password"),
        ("noc.influx_user", "influxdb.user"),
        ("noc.ch_db", "clickhouse.db"),
        ("noc.ch_user", "clickhouse.rw_user"),
        ("noc.ch_password", "clickhouse.rw_password"),
        ("noc.ch_ro_password", "clickhouse.ro_password"),
        ("noc-global-%(node)s.python_interpreter", "features.pypy"),

        # Activator
        ("activator.script_threads", "activator.script_threads"),
        ("activator-%(pool)s-%(node)s.script_threads", "activator.script_threads"),
        ("activator.tos", "activator.tos"),
        ("activator-%(pool)s-%(node)s.tos", "activator.tos"),
        # Bi
        ("bi.language", "bi.language"),
        ("bi-global-%(node)s.language", "bi.language"),
        ("bi.query_threads", "bi.query_threads"),
        ("bi-global-%(node)s.query_threads", "bi.query_threads"),
        # Card
        ("card.language", "card.language"),
        ("card-global-%(node)s.language", "card.language"),
        # Chwriter
        ("chwriter.batch_delay_ms", "chwriter.batch_delay_ms"),
        ("chwriter-global-%(node)s.batch_delay_ms", "chwriter.batch_delay_ms"),
        ("chwriter.batch_size", "chwriter.batch_size"),
        ("chwriter-global-%(node)s.batch_size", "chwriter.batch_size"),
        ("chwriter.channel_expire_interval", "chwriter.channel_expire_interval"),
        ("chwriter-global-%(node)s.channel_expire_interval", "chwriter.channel_expire_interval"),
        ("chwriter.records_buffer", "chwriter.records_buffer"),
        ("chwriter-global-%(node)s.records_buffer", "chwriter.records_buffer"),
        # Classifier
        ("classifier.default_interface_profile", "classifier.default_interface_profile"),
        ("classifier-%(pool)s-%(node)s.default_interface_profile", "classifier.default_interface_profile"),
        ("classifier.lookup_solution", "classifier.lookup_handler"),
        ("classifier-%(pool)s-%(node)s.lookup_solution", "classifier.lookup_handler"),
        # Correlator
        ("correlator.max_threads", "correlator.max_threads"),
        ("correlator-%(pool)s-%(node)s.max_threads", "correlator.max_threads"),
        # Discovery
        ("discovery.max_threads", "discovery.max_threads"),
        ("discovery-%(pool)s-%(node)s.max_threads", "discovery.max_threads"),
        # Escalator
        ("escalator.max_threads", "escalator.max_threads"),
        ("escalator-global-%(node)s.max_threads", "escalator.max_threads"),
        # Grafanads
        ("grafanads.db_threads", "grafanads.db_threads"),
        ("grafanads-global-%(node)s.db_threads", "grafanads.db_threads"),
        # Login
        ("login.language", "login.language"),
        ("login-global-%(node)s.language", "login.language"),
        ("login.methods", "login.methods"),
        ("login-global-%(node)s.methods", "login.methods"),
        ("login.pam_service", "login.pam_service"),
        ("login-global-%(node)s.pam_service", "login.pam_service"),
        ("login.radius_server", "login.radius_server"),
        ("login-global-%(node)s.radius_server", "login.radius_server"),
        ("login.session_ttl", "login.session_ttl"),
        ("login-global-%(node)s.session_ttl", "login.session_ttl"),
        # Mailsender
        ("mailsender.from_address", "mailsender.from_address"),
        ("mailsender-global-%(node)s.from_address", "mailsender.from_address"),
        ("mailsender.helo_hostname", "mailsender.helo_hostname"),
        ("mailsender-global-%(node)s.helo_hostname", "mailsender.helo_hostname"),
        ("mailsender.smtp_password", "mailsender.smtp_password"),
        ("mailsender-global-%(node)s.smtp_password", "mailsender.smtp_password"),
        ("mailsender.smtp_port", "mailsender.smtp_port"),
        ("mailsender-global-%(node)s.smtp_port", "mailsender.smtp_port"),
        ("mailsender.smtp_server", "mailsender.smtp_server"),
        ("mailsender-global-%(node)s.smtp_server", "mailsender.smtp_server"),
        ("mailsender.smtp_user", "mailsender.smtp_user"),
        ("mailsender-global-%(node)s.smtp_user", "mailsender.smtp_user"),
        ("mailsender.use_tls", "mailsender.use_tls"),
        ("mailsender-global-%(node)s.use_tls", "mailsender.use_tls"),
        # mrt
        ("mrt.max_concurrency", "mrt.max_concurrency"),
        ("mrt-global-%(node)s.max_concurrency", "mrt.max_concurrency"),
        # ping
        ("ping.restore_threshold", "ping.restore_threshold"),
        ("ping-%(pool)s-%(node)s.restore_threshold", "ping.restore_threshold"),
        ("ping.throttle_threshold", "ping.throttle_threshold"),
        ("ping-%(pool)s-%(node)s.throttle_threshold", "ping.throttle_threshold"),
        ("ping.tos", "ping.tos"),
        ("ping-%(pool)s-%(node)s.tos", "ping.tos"),
        ("ping.global_n_instances", "global_n_instances"),
        ("ping-%(pool)s-%(node)s.global_n_instances", "global_n_instances"),
        # Pmwriter
        ("pmwriter.batch_size", "pmwriter.batch_size"),
        ("pmwriter-global-%(node)s.batch_size", "pmwriter.batch_size"),
        ("pmwriter.metrics_buffer", "pmwriter.metrics_buffer"),
        ("pmwriter-global-%(node)s.metrics_buffer", "pmwriter.metrics_buffer"),
        # SAE
        ("sae.db_threads", "sae.db_threads"),
        ("sae-global-%(node)s.db_threads", "sae.db_threads"),
        # Scheduler
        ("scheduler.max_threads", "scheduler.max_threads"),
        ("scheduler-global-%(node)s.max_threads", "scheduler.max_threads"),
        # SyslogCollector
        ("syslogcollector.listen_syslog", "syslogcollector.listen"),
        ("syslogcollector-%(pool)s-%(node)s.listen_syslog", "syslogcollector.listen"),
        # TgSender
        ("tgsender.token", "tgsender.token"),
        ("tgsender-global-%(node)s.token", "tgsender.token"),
        # TrapCollector
        ("trapcollector.listen_traps", "trapcollector.listen"),
        ("trapcollector-%(pool)s-%(node)s.listen_traps", "trapcollector.listen"),
        # Web
        ("web.language", "web.language"),
        ("web-global-%(node)s.language", "web.language"),
        ("web.max_threads", "web.max_threads"),
        ("web-global-%(node)s.max_threads", "web.max_threads")

    ]

    def __init__(self, config, url):
        super(LegacyProtocol, self).__init__(config, url)
        if self.parsed_url.path == "/":
            self.path = config.path.legacy_config
        else:
            self.path = self.parsed_url.path

    def load(self):
        def get_path(conf, key):
            d = conf
            parts = key.split(".")
            for p in parts:
                d = d.get(p)
                if d is None:
                    break
            return d

        if not os.path.exists(self.path):
            return
        logger.info("Legacy config will be deprecated after 1 June 2018. "
                    "Please update tower and remove from used config options.")
        with open(self.path) as f:
            data = yaml.load(f)["config"]
        for legacy_key, new_key in self.NOC_MAPPINGS:
            v = get_path(data, legacy_key % {"node": self.config.node, "pool": self.config.pool})
            if v is not None:
                self.config.set_parameter(
                    new_key,
                    v
                )
            if 'features.pypy' in new_key:
                if v and 'pypy' in v:
                    self.config.set_parameter(
                        new_key,
                        True
                    )
