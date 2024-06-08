# ---------------------------------------------------------------------
# inv.configuredmap application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.inv.models.configuredmap import ConfiguredMap, ObjectFilter
from noc.core.translation import ugettext as _


class ConfiguredMapApplication(ExtDocApplication):
    """
    ConnectionType application
    """

    title = _("Configured Map")
    menu = [_("Setup"), _("Configured Maps")]
    model = ConfiguredMap
    query_fields = ["name__icontains"]

    def instance_to_dict(self, o: "ConfiguredMap", fields=None, nocustom=False):
        if isinstance(o, ObjectFilter):
            return o
        r = {
            "id": str(o.id),
            "name": o.name,
            "layout": o.layout,
            "width": o.width,
            "height": o.height,
            "status_filter": [],
            "add_linked_node": o.add_linked_node,
            "add_topology_links": o.add_topology_links,
            "enable_node_portal": o.enable_node_portal,
            "background_image": None,
            "nodes": [],
            "links": [],
        }
        if o.background_image:
            r["background_image"] = str(o.background_image.id)
            r["background_image__label"] = o.background_image.name
        node_map = {}
        for nn in o.nodes:
            node = super().instance_to_dict(nn)
            title = node["title"]
            object_filter = node.pop("object_filter", None)
            if object_filter and object_filter.managed_object:
                # mo = ManagedObject.get_by_id(int(ref_id))
                node["managed_object"] = object_filter.managed_object.id
                node["managed_object__label"] = object_filter.managed_object.name
                title = title or object_filter.managed_object.name
            if object_filter and object_filter.resource_group:
                # rg = ResourceGroup.get_by_id(ref_id)
                node["resource_group"] = str(object_filter.resource_group.id)
                node["resource_group__label"] = object_filter.resource_group.name
                title = title or object_filter.resource_group.name
            if object_filter and object_filter.segment:
                # ns = NetworkSegment.get_by_id(ref_id)
                node["segment"] = str(object_filter.segment.id)
                node["segment__label"] = object_filter.segment.name
                title = title or object_filter.segment.name
            if object_filter and object_filter.container:
                # ns = NetworkSegment.get_by_id(ref_id)
                node["container"] = str(object_filter.container.id)
                node["container__label"] = object_filter.container.name
                title = title or object_filter.container.name
            node_map[str(nn.node_id)] = title
            r["nodes"].append(node)
        for ll in o.links:
            ll = super().instance_to_dict(ll)
            if ll["source_node"]:
                ll["source_node"] = {
                    "id": str(ll["source_node"]),
                    "label": node_map.get(ll["source_node"], ""),
                }
            ll["target_nodes"] = [
                {"id": str(tn), "label": node_map.get(str(tn), "")}
                for tn in ll.get("target_nodes", [])
            ]
            r["links"].append(ll)
        return r

    def clean(self, data):
        for node in data.get("nodes", []):
            mo = node.pop("managed_object", None)
            rg = node.pop("resource_group", None)
            sg = node.pop("segment", None)
            cnt = node.pop("container", None)
            object_filter = {}
            if node["node_type"] in {"managedobject", "other"} and mo:
                object_filter["managed_object"] = mo
            if node["node_type"] in {"objectgroup", "other"} and rg:
                object_filter["resource_group"] = rg
            if node["node_type"] in {"objectsegment", "other"} and sg:
                object_filter["segment"] = sg
            if node["node_type"] in {"container", "other"} and cnt:
                object_filter["container"] = cnt
            node["object_filter"] = object_filter or None
        return super().clean(data)

    @view(r"^(?P<map_id>[0-9a-f]{24})/nodes/$", method=["GET"], access="read", api=True)
    def get_map_nodes(self, request, map_id):
        r = []
        rid = request.GET.getlist("id")
        o = ConfiguredMap.get_by_id(map_id)
        for node in o.nodes:
            if rid and str(node.node_id) not in rid:
                continue
            r.append({"label": node.title, "id": str(node.node_id)})
        return r
