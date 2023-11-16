# ---------------------------------------------------------------------
# Configuration Param discovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import List
from collections import namedtuple

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.object import Object
from noc.cm.models.configurationparam import ParamData, ScopeVariant

SRC_INTERFACE = "i"
SRC_MPLS = "m"
SRC_MANUAL = "M"
SRC_CONFDB = "c"

PREF_VALUE = {SRC_INTERFACE: 0, SRC_MPLS: 1, SRC_CONFDB: 2, SRC_MANUAL: 3}


class ConfigParamCheck(DiscoveryCheck):
    name = "configparam"

    get_param_script = "get_params_data"

    def handler(self):
        r: List[ParamData] = []
        r += self.get_param_data_confdb()
        r += self.get_param_data_artifact()
        r += self.get_param_data_script()

    def is_enabled(self):
        enabled = super().is_enabled()
        if not enabled:
            return False
        o = Object.get_managed(self.object)
        return o and o.model.configuration_rule

    def get_param_data_confdb(self) -> List[ParamData]:
        """
        Getting Config Param Data from ConfDB
        :return:
        """
        self.logger.debug("Getting ParamData from ConfDB")
        confdb = self.get_confdb()
        if confdb is None:
            self.logger.error("ConfDB artefact is not set. Skipping ConfDB Params")
            return []
        return []

    def get_param_data_artifact(self) -> List[ParamData]:
        """
        Getting Config Param Data from Artifacts
        :return:
        """
        self.logger.debug("Getting ParamData from Artifacts")
        params = self.get_artefact("config_param_data")
        if not params:
            self.logger.info("No interface_vpn artefact, skipping interface prefixes")
            return []
        r = []
        for p in params:
            scopes = [ScopeVariant.from_code(p["scope"])]
            r.append(
                ParamData(code=p["param"], value=p["value"], scopes=scopes, schema=None)
            )
        return r

    def get_param_data_script(self) -> List[ParamData]:
        """
        Getting Config Param Data from script
        :return:
        """
        self.logger.debug("Getting ParamData from script")
        if self.get_param_script not in self.object.scripts:
            self.logger.info("Script '%s' is not supported. Skipping...", self.get_param_script)
            return []
        r = []
        params = self.object.scripts.get_params_data()
        for p in params:
            scopes = [ScopeVariant.from_code(p["scope"])]
            r.append(
                ParamData(code=p["param"], value=p["value"], scopes=scopes, schema=None)
            )
        return r
