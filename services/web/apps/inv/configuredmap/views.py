# ---------------------------------------------------------------------
# inv.configuredmap application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.inv.models.configuredmap import ConfiguredMap
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.networksegment import NetworkSegment
from noc.core.translation import ugettext as _


class ConfiguredMapApplication(ExtDocApplication):
    """
    ConnectionType application
    """

    title = _("Configured Map")
    menu = [_("Setup"), _("Configured Maps")]
    model = ConfiguredMap
    query_fields = ["name__icontains"]

    def instance_to_dict(self, o, fields=None, nocustom=False):
        v = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        for node in v.get("nodes", []):
            if node["node_type"] == "managedobject":
                mo = ManagedObject.get_by_id(int(node["reference_id"]))
                node["managed_object"] = mo.id
                node["managed_object__label"] = mo.name
            elif node["node_type"] == "group":
                rg = ResourceGroup.get_by_id(node["reference_id"])
                node["resource_group"] = rg.id
                node["resource_group__label"] = rg.name
            elif node["node_type"] == "group":
                ns = NetworkSegment.get_by_id(node["reference_id"])
                node["segment_group"] = ns.id
                node["segment__label"] = ns.name
        return v

    def clean(self, data):
        for node in data.get("nodes", []):
            mo = node.pop("managed_object", None)
            rg = node.pop("resource_group", None)
            sg = node.pop("segment", None)
            if node["node_type"] == "managedobject":
                node["reference_id"] = str(mo)
            elif node["node_type"] == "group":
                node["reference_id"] = rg
            elif node["node_type"] == "segment":
                node["reference_id"] = sg
        return super().clean(data)

    @view(r"^(?P<map_id>[0-9a-f]{24})/nodes/$", method=["GET"], access="read", api=True)
    def get_map_nodes(self, request, map_id):
        r = []
        o = ConfiguredMap.objects.filter(id=map_id).first()
        for node in o.nodes:
            r.append({"label": node.title, "id": str(node.node_id)})
        return r
