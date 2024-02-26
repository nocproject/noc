# ---------------------------------------------------------------------
# inv.inv param data plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, List, Any

# NOC modules
from noc.inv.models.object import Object
from noc.cm.models.configurationparam import ConfigurationParam
from noc.sa.interfaces.base import StringParameter, StringListParameter, DictListParameter
from .base import InvPlugin


class ParamPlugin(InvPlugin):
    name = "param"
    js = "NOC.inv.inv.plugins.param.ParamPanel"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            "api_plugin_%s_save_data" % self.name,
            self.api_save_data,
            url="^(?P<id>[0-9a-f]{24})/plugin/param/$",
            method=["PUT"],
            validate=DictListParameter(
                attrs={
                    "param": StringParameter(),
                    "scopes": StringListParameter(required=False),
                    "value": StringParameter(default="", required=False),
                },
            ),
        )
        self.add_view(
            "api_plugin_%s_schema" % self.name,
            self.api_save_data,
            url="^(?P<id>[0-9a-f]{24})/plugin/param/schema/$",
            method=["GET"],
            validate={
                "param": StringParameter(),
                "scope": StringParameter(),
            },
        )
        self.add_view(
            "api_plugin_%s_scopes" % self.name,
            self.api_scopes,
            url="^(?P<id>[0-9a-f]{24})/plugin/param/scopes/$",
            method=["GET"],
        )

    def get_data(self, request, o: Object):
        data = []
        q = self.app.parse_request_query(request)
        scopes = set()
        if "scope" in q:
            scopes = set(q["scope"].split(","))
        for cd in o.get_effective_cfg_params():
            if scopes and cd.scope not in scopes:
                continue
            param = ConfigurationParam.get_by_code(cd.code)
            data += [
                {
                    "param": str(param.id),
                    "param__label": param.name,
                    "value": cd.value,
                    "type": cd.schema.type,
                    "description": param.description,
                    "is_readonly": cd.value and cd.schema.choices and len(cd.schema.choices) == 1,
                    "choices": cd.schema.choices,
                    "scope": cd.scope,
                    "scope__label": " ".join(s.code for s in cd.scopes),
                }
            ]
            data[-1].update(cd.schema.json_schema)
        return {"id": str(o.id), "name": o.name, "model": o.model.name, "data": data}

    def api_save_data(self, request, id, **kwargs):
        o: "Object" = self.app.get_object_or_404(Object, id=id)
        data: List[Dict[str, Any]] = self.app.deserialize(request.body)
        for d in data:
            p = self.app.get_object_or_404(ConfigurationParam, id=d["param"])
            if not d.get("scopes"):
                o.set_cfg_data(p, d["value"])
            else:
                for s in d["scopes"]:
                    o.set_cfg_data(
                        p, d["value"], scope=s, is_dirty=True
                    )  # scopes=s[1:].split("@"))
        try:
            o.save()
        except Exception as e:
            return {"status": False, "message": str(e), "traceback": str(e)}
        return {"status": True}

    def api_scopes(self, request, id, **kwargs):
        """"""
        o = self.app.get_object_or_404(Object, id=id)
        scopes = set()
        for p in o.get_effective_cfg_params():
            if not p.scopes:
                continue
            scopes |= set(s.code for s in p.scopes)
        return [{"id": f"@{s}", "label": s} for s in scopes]

    # def api_get_schema(self, request, id, param=None, scope: Optional[str] = None):
    #     """
    #     Getting Param Schema
    #     """
    #     o = self.app.get_object_or_404(Object, id=id)
    #     param = self.app.get_object_or_404(ConfigurationParam, id=param)
    #     return param.get_schema(o)
