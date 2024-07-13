# ---------------------------------------------------------------------
# inv.inv channel plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.inv.models.object import Object
from noc.core.techdomain.tracer.base import BaseTracer
from noc.sa.interfaces.base import ObjectIdParameter, StringParameter
from noc.core.techdomain.tracer.loader import loader as tracer_loader
from .base import InvPlugin


class ChannelPlugin(InvPlugin):
    name = "channel"
    js = "NOC.inv.inv.plugins.channel.ChannelPanel"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            "api_plugin_%s_get_adhoc_list" % self.name,
            self.api_get_adhoc_list,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/adhoc/$" % self.name,
            method=["GET"],
        )
        self.add_view(
            "api_plugin_%s_create_adhoc" % self.name,
            self.api_create_adhoc,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/adhoc/$" % self.name,
            method=["POST"],
            validate={"object": ObjectIdParameter(), "tracer": StringParameter()},
        )

    def get_data(self, request, object):
        # @todo: Write implementation
        return {
            "records": [
                {
                    "id": "1" * 24,
                    "name": "Ch1",
                    "tech_domain": "444",
                    "tech_domain__label": "Optical SM",
                },
                {
                    "id": "2" * 24,
                    "name": "Ch2",
                    "tech_domain": "444",
                    "tech_domain__label": "Optical SM",
                },
            ]
        }

    def object_label(self, obj: Object) -> str:
        """
        Get readable object name
        """
        local_name = obj.get_local_name_path(True)
        if local_name:
            return " | ".join(local_name)
        return obj.name

    def oblect_and_model_label(self, obj: Object) -> str:
        return f"{self.object_label(obj)} [{obj.model.get_short_label()}]"

    def api_get_adhoc_list(self, request, id):
        o = self.app.get_object_or_404(Object, id=id)
        nested_objects = list(BaseTracer().iter_nested_objects(o))
        r = []
        # Check all tracers
        for tr_name in tracer_loader:
            tr = tracer_loader[tr_name]()
            for no in nested_objects:
                if tr.is_ad_hoc_available(no):
                    r += [
                        {
                            "object": str(no.id),
                            "object__label": self.oblect_and_model_label(no),
                            "tracer": tr.name,
                        }
                    ]
        return r

    def api_create_adhoc(self, request, id, object, tracer):
        self.app.get_object_or_404(Object, id=id)
        obj = self.app.get_object_or_404(Object, id=object)
        tr = tracer_loader[tracer]()
        ch, msg = tr.sync_ad_hoc_channel(obj)
        r = {"status": ch is not None, "msg": msg}
        if ch:
            r["channel"] = str(ch.id)
        return r
