# ---------------------------------------------------------------------
# Configuration Param discovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import List, Dict, Any, Tuple

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.object import Object
from noc.cm.models.configurationparam import ConfigurationParam, ParamData, ScopeVariant


class ConfigParamCheck(DiscoveryCheck):
    name = "configparam"

    get_param_script = "get_params_data"

    def handler(self):
        chassis = Object.get_managed(self.object)
        chassis_data = self.get_param_data_confdb(chassis)
        chassis_data += self.get_param_data_script(chassis)
        if chassis_data:
            self.submit_param_data(chassis, chassis_data)
        for o, data in self.get_param_data_artifact(chassis):
            self.submit_param_data(o, data)

    def submit_param_data(self, o: "Object", data):
        """ """
        ed: Dict[ParamData, Any] = {}
        for pd in o.get_effective_cfg_params():
            ed[pd] = pd.value
        self.logger.info("[%s] Submit Param Data", o)
        for pd in data:
            if pd not in ed:
                pass
            elif ed[pd] == pd.value:
                # Same value
                continue
            elif ed[pd] is not None:
                # Resolve conflict when discovery diff value from object,
                # Resolve from policy
                if (
                    self.object.object_profile.box_discovery_param_data_conflict_resolve_policy
                    == "M"
                ):
                    # Manual conflict
                    o.set_cfg_data(pd.param, pd.value, pd.scope, is_conflicted=True)
                    continue
                elif (
                    self.object.object_profile.box_discovery_param_data_conflict_resolve_policy
                    == "O"
                ):
                    # Set param is_dirty
                    o.set_cfg_data(pd.param, ed[pd], pd.scope, is_dirty=True)
                    continue
            try:
                o.set_cfg_data(pd.param, pd.value, pd.scope, is_dirty=True)
            except (AttributeError, ValueError) as e:
                self.logger.warning(
                    "[%s|%s|%s] Error when set param: %s", pd.param, pd.scope, pd.value, str(e)
                )
                continue
            o.log(
                f"Object param '{pd.param}' changed: {ed.get(pd)} -> {pd.value}",
                system="DISCOVERY",
                managed_object=self.object,
                op="PARAM_CHANGED",
            )
            # Set Last Seen
        o.save()

    def clean_result(self, o: Object, data: List[Dict[str, Any]]) -> List["ParamData"]:
        r = []
        for d in data:
            param = ConfigurationParam.get_by_code(d["param"])
            if not param:
                self.logger.error("[%s] Unknown param. Skipping...", d["param"])
                continue
            scopes = []
            for s in d.get("scopes", []):
                if s.get("value") is None:
                    scopes.append(ScopeVariant.from_code(s["scope"]))
                else:
                    scopes.append(ScopeVariant.from_code(f"{s['scope']}::{s['value']}"))
            schema = param.get_schema(o)
            try:
                value = schema.clean(d["value"])
            except ValueError:
                self.logger.error("[%s] Bad value: %s", param, d["value"])
                continue
            r.append(ParamData(code=param.code, value=value, scopes=scopes, schema=schema))
        return r

    def is_enabled(self):
        enabled = super().is_enabled()
        if not enabled:
            return False
        o = Object.get_managed(self.object)
        return bool(o)

    def get_param_data_confdb(self, o: Object) -> List["ParamData"]:
        """
        Getting Config Param Data from ConfDB
        :param o: Chassis Object
        :return:
        """
        self.logger.debug("Getting ParamData from ConfDB")
        confdb = self.get_confdb()
        if confdb is None:
            self.logger.error("ConfDB artefact is not set. Skipping ConfDB Params")
            return []
        return []

    def get_param_data_artifact(self, o: Object) -> List[Tuple["Object", List["ParamData"]]]:
        """
        Getting Config Param Data from Artifacts
        :param o: Chassis Object
        :return:
        """
        self.logger.debug("Getting ParamData from Artifacts")
        o_artifacts: Dict[str, List[Dict[str, Any]]] = self.get_artefact("object_param_artifacts")
        if not o_artifacts:
            self.logger.info("No object asset artifacts, skipping object param data")
            return []
        r = []
        for o, params in o_artifacts.items():
            o = Object.get_by_id(o)
            if not o:
                continue
            r.append((o, self.clean_result(o, params)))
        return r

    def get_param_data_script(self, o: Object) -> List["ParamData"]:
        """
        Getting Config Param Data from script
        :param o: Chassis Object
        :return:
        """
        self.logger.debug("Getting ParamData from script")
        if self.get_param_script not in self.object.scripts:
            self.logger.info("Script '%s' is not supported. Skipping...", self.get_param_script)
            return []
        r = self.object.scripts.get_params_data()
        return self.clean_result(o, r)
