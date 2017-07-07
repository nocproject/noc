# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Load legacy noc.yml
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
# Third-party modules
import yaml
# NOC modules
from base import BaseProtocol


class LegacyProtocol(BaseProtocol):
    """
    Load legacy noc.yml file
    Usage:

    legacy:///
    """
    PATH = "etc/noc.yml"
    NOC_MAPPINGS = {
        "noc.installation_name": "installation_name",
        "noc.language": "language",
        "noc.mongo_password": "mongo.password",
        "noc.mongo_user": "mongo.user",
        "noc.mongo_rs": "mongo.rs",
        "noc.mongo_db": "mongo.db",
        "noc.pg_db": "pg.db",
        "noc.pg_password": "pg.password",
        "pg_user": "pg.user",
        "activator.script_threads": "activator.script_threads",
        "activator.tos": "activator.tos",
        "bi.language": "bi.language",
        "bi.query_threads": "bi.query_threads",
        #
        "web.max_treads": "web.max_threads",
        "web.language": "web.language",
        "login.language": "login.language",
        "discovery.max_threads": "discovery.max_threads",
        "classifier.lookup_solution": "classifier.lookup_handler."

    }

    def load(self):
        def get_path(d, key):
            parts = key.split(".")
            if parts[0] == "noc" or "-" not in parts[0]:
                # Global config
                for p in parts:
                    if p not in d:
                        return None
                    d = d[p]
                return d
            else:
                # Service config
                selector = "%s-%s-%s" % (parts[0], svc_pool, svc_node)
                if selector not in d:
                    return None
                d = d[selector]
                for p in parts[1:]:
                    if p not in d:
                        return None
                    d = d[p]
                return d

        svc_pool = os.environ.get("NOC_POOL", "")
        svc_node = os.environ.get("NOC_NODE", "")

        with open(self.PATH) as f:
            data = yaml.load(f)["config"]
        for legacy_key in self.NOC_MAPPINGS:
            v = get_path(data, legacy_key)
            if v is not None:
                self.config.set_parameter(
                    self.NOC_MAPPINGS[legacy_key],
                    v
                )
