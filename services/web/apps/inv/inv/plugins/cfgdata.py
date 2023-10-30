# ---------------------------------------------------------------------
# inv.inv configdata plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, List, Optional, Any

# NOC modules
from noc.inv.models.object import Object
from noc.cm.models.configurationparam import ConfigurationParam
from noc.sa.interfaces.base import StringParameter
from .base import InvPlugin


class CfgDataPlugin(InvPlugin):
    name = "cfgdata"
    js = "NOC.inv.inv.plugins.data.CfgDataPanel"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            "api_plugin_%s_save_data" % self.name,
            self.api_save_data,
            url="^(?P<id>[0-9a-f]{24})/plugin/cfgdata/$",
            method=["PUT"],
            validate={
                "param": StringParameter(),
                "scope": StringParameter(),
                "value": StringParameter(default="", required=False),
            },
        )
        self.add_view(
            "api_plugin_%s_schema" % self.name,
            self.api_save_data,
            url="^(?P<id>[0-9a-f]{24})/plugin/cfgdata/schema/$",
            method=["GET"],
            validate={
                "param": StringParameter(),
                "scope": StringParameter(),
            },
        )

    def get_data(self, request, o: Object):
        data = []
        for cd in o.cfg_data:
            data += [
                {
                    "param": str(cd.param.id),
                    "param__label": cd.param.name,
                    "value": cd.value,
                    "type": cd.param.type,
                    "description": cd.param.description,
                    "is_readonly ": False,
                    "choices": None,
                    "scope": cd.scope,
                    "scope__label": cd.scope,
                }
            ]
        return {"id": str(o.id), "name": o.name, "model": o.model.name, "data": data}

    def api_save_data(self, request, oid, data: List[Dict[str, Any]]):
        o = self.app.get_object_or_404(Object, id=oid)
        for d in data:
            param = self.app.get_object_or_404(ConfigurationParam, id=d["param"])
            for s in d["scopes"]:
                o.set_cfg_data(param, s, d["value"])

    def api_get_schema(self, request, oid, param=None, scope: Optional[str] = None):
        """
        Getting Param Schema
        """
        o = self.app.get_object_or_404(Object, id=oid)
        param = self.app.get_object_or_404(ConfigurationParam, id=param)
        return param.get_schema(o)
