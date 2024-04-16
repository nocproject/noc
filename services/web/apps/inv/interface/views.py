# ---------------------------------------------------------------------
# inv.interface application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine import Q

# NOC modules
from noc.services.web.base.decorators.state import state_handler
from noc.services.web.base.extapplication import view
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.sa.interfaces.base import (
    StringParameter,
    ListOfParameter,
    DocumentParameter,
    ModelParameter,
)
from noc.project.models.project import Project
from noc.core.text import alnum_key, list_to_ranges
from noc.core.translation import ugettext as _
from noc.config import config
from noc.core.comp import smart_text


@state_handler
class InterfaceAppplication(ExtDocApplication):
    """
    inv.interface application
    """

    title = _("Interfaces")
    menu = _("Interfaces")
    model = Interface
    query_fields = ["description__contains"]

    mrt_config = {
        "get_mac": {
            "map_script": "get_mac_address_table",
            "timeout": config.script.timeout,
            "access": "get_mac",
        }
    }

    implied_permissions = {
        "get_mac": [
            "inv:inv:read",
            "inv:interface:view",
            "sa:managedobject:lookup",
            "sa:managedobject:read",
        ]
    }

    def get_Q(self, request, query):
        return super().get_Q(request, query)

    @staticmethod
    def get_style(i: Interface):
        profile = i.profile
        # try:
        #     return style_cache[profile.id]
        # except KeyError:
        #     pass
        if profile.style:
            s = profile.style.css_class_name
        else:
            s = ""
        # style_cache[profile.id] = s
        return s

    @staticmethod
    def get_link(i: Interface):
        link = i.link
        if not link:
            return None
        if link.is_ptp:
            # ptp
            o = link.other_ptp(i)
            label = f"{o.managed_object.name}:{o.name}"
        elif link.is_lag:
            # unresolved LAG
            o = [ii for ii in link.other(i) if ii.managed_object.id != i.managed_object.id]
            label = f'LAG {o[0].managed_object.name}: {", ".join(ii.name for ii in o)}'
        else:
            # Broadcast
            label = ", ".join(f"{ii.managed_object.name}:{ii.name}" for ii in link.other(i))
        return {"id": str(link.id), "label": label}

    def get_subinterface(self, si: SubInterface):
        r = {
            "name": si.name,
            "description": si.description,
            "untagged_vlan": si.untagged_vlan,
            "tagged_vlans": list_to_ranges(si.tagged_vlans),
            "ipv4_addresses": si.ipv4_addresses,
            "ipv6_addresses": si.ipv6_addresses,
            "enabled_protocols": si.enabled_protocols,
            "vlan": si.vlan_ids,
            "project": si.project.id if si.project else None,
            "project__label": str(si.project) if si.project else None,
            "l2_domain": str(si.l2_domain.id) if si.l2_domain else None,
            "l2_domain__label": str(si.l2_domain) if si.l2_domain else None,
            "vrf": si.forwarding_instance.name if si.forwarding_instance else "",
            "service": str(si.service.id) if si.service else None,
            "service__label": str(si.service) if si.service else None,
        }
        return r

    def instance_to_dict(self, o: Interface, fields=None, nocustom=False):
        r = {
            "id": str(o.id),
            "name": o.name,
            "description": o.description,
            "mac": o.mac,
            "managed_object": o.managed_object.id,
            "managed_object__label": str(o.managed_object.name),
            "ifindex": o.ifindex,
            "lag": (o.aggregated_interface.name if o.aggregated_interface else ""),
            "link": None,
            "link__label": "",
            "profile": str(o.profile.id) if o.profile else None,
            "profile__label": str(o.profile) if o.profile else "",
            "enabled_protocols": o.enabled_protocols,
            "project": str(o.project.id) if o.project else None,
            "project__label": str(o.project) if o.project else "",
            "state": str(o.state.id) if o.state else None,
            "state__label": str(o.state) if o.state else "",
            "service": str(o.service.id) if o.service else None,
            "service__label": str(o.service) if o.service else "",
            "row_class": self.get_style(o),
            "subinterfaces": [self.get_subinterface(si) for si in o.subinterface_set],
        }
        link = self.get_link(o)
        if link:
            r["link"] = link["id"]
            r["link__label"] = link["label"]
        return r

    @view(url=r"^(?P<managed_object>\d+)/$", method=["GET"], access="view", api=True)
    def api_get_interfaces(self, request, managed_object):
        """
        GET interfaces
        :param managed_object:
        :return:
        """

        def sorted_iname(s):
            return list(sorted(s, key=lambda x: alnum_key(x["name"])))

        # Get object
        o = self.get_object_or_404(ManagedObject, id=int(managed_object))
        if not o.has_access(request.user):
            return self.response_forbidden("Permission denied")
        # Physical interfaces
        # @todo: proper ordering
        # style_cache = {}  # profile_id -> css_style
        l1 = [
            {
                "id": str(i.id),
                "name": i.name,
                "description": i.description,
                "mac": i.mac,
                "ifindex": i.ifindex,
                "lag": (i.aggregated_interface.name if i.aggregated_interface else ""),
                "link": self.get_link(i),
                "profile": str(i.profile.id) if i.profile else None,
                "profile__label": smart_text(i.profile) if i.profile else None,
                "enabled_protocols": i.enabled_protocols,
                "project": i.project.id if i.project else None,
                "project__label": smart_text(i.project) if i.project else None,
                "state": str(i.state.id) if i.state else None,
                "state__label": smart_text(i.state) if i.state else None,
                "row_class": self.get_style(i),
            }
            for i in Interface.objects.filter(managed_object=o.id, type="physical")
        ]
        # LAG
        lag = [
            {
                "id": str(i.id),
                "name": i.name,
                "description": i.description,
                "members": [
                    j.name
                    for j in Interface.objects.filter(
                        managed_object=o.id, aggregated_interface=i.id
                    )
                ],
                "profile": str(i.profile.id) if i.profile else None,
                "profile__label": smart_text(i.profile) if i.profile else None,
                "enabled_protocols": i.enabled_protocols,
                "project": i.project.id if i.project else None,
                "project__label": smart_text(i.project) if i.project else None,
                "state": str(i.state.id) if i.state else None,
                "state__label": smart_text(i.state) if i.state else None,
                "row_class": self.get_style(i),
            }
            for i in Interface.objects.filter(managed_object=o.id, type="aggregated")
        ]
        # L2 interfaces
        l2 = [
            {
                "name": i.name,
                "description": i.description,
                "untagged_vlan": i.untagged_vlan,
                "tagged_vlans": i.tagged_vlans,
            }
            for i in SubInterface.objects.filter(managed_object=o.id, enabled_afi="BRIDGE")
        ]
        # L3 interfaces
        q = Q(enabled_afi="IPv4") | Q(enabled_afi="IPv6")
        l3 = [
            {
                "name": i.name,
                "description": i.description,
                "ipv4_addresses": i.ipv4_addresses,
                "ipv6_addresses": i.ipv6_addresses,
                "enabled_protocols": i.enabled_protocols,
                "vlan": i.vlan_ids,
                "vrf": i.forwarding_instance.name if i.forwarding_instance else "",
            }
            for i in SubInterface.objects.filter(managed_object=o.id).filter(q)
        ]
        return {
            "l1": sorted_iname(l1),
            "lag": sorted_iname(lag),
            "l2": sorted_iname(l2),
            "l3": sorted_iname(l3),
        }

    @view(
        url=r"^link/$",
        method=["POST"],
        validate={
            "type": StringParameter(choices=["ptp"]),
            "interfaces": ListOfParameter(element=DocumentParameter(Interface)),
        },
        access="link",
        api=True,
    )
    def api_link(self, request, type, interfaces):
        if type == "ptp":
            if len(interfaces) == 2:
                interfaces[0].link_ptp(interfaces[1])
                return {"status": True}
            else:
                raise ValueError("Invalid interfaces length")
        return {"status": False}

    @view(url=r"^unlink/(?P<iface_id>[0-9a-f]{24})/$", method=["POST"], access="link", api=True)
    def api_unlink(self, request, iface_id):
        i = Interface.objects.filter(id=iface_id).first()
        if not i:
            return self.response_not_found()
        try:
            i.unlink()
            return {"status": True, "msg": "Unlinked"}
        except ValueError as why:
            return {"status": False, "msg": str(why)}

    @view(url=r"^unlinked/(?P<object_id>\d+)/$", method=["GET"], access="link", api=True)
    def api_unlinked(self, request, object_id):
        def get_label(i):
            if i.description:
                return "%s (%s)" % (i.name, i.description)
            else:
                return i.name

        o = self.get_object_or_404(ManagedObject, id=int(object_id))
        r = [
            {"id": str(i.id), "label": get_label(i)}
            for i in Interface.objects.filter(managed_object=o.id, type="physical").order_by("name")
            if not i.link
        ]
        return list(sorted(r, key=lambda x: alnum_key(x["label"])))

    @view(
        url=r"^l1/(?P<iface_id>[0-9a-f]{24})/change_profile/$",
        validate={"profile": DocumentParameter(InterfaceProfile)},
        method=["POST"],
        access="profile",
        api=True,
    )
    def api_change_profile(self, request, iface_id, profile):
        i = Interface.objects.filter(id=iface_id).first()
        if not i:
            return self.response_not_found()
        if i.profile != profile:
            i.profile = profile
            i.profile_locked = True
            i.save()
        return True

    @view(
        url=r"^l1/(?P<iface_id>[0-9a-f]{24})/change_project/$",
        validate={"project": ModelParameter(Project, required=False)},
        method=["POST"],
        access="profile",
        api=True,
    )
    def api_change_project(self, request, iface_id, project):
        i = Interface.objects.filter(id=iface_id).first()
        if not i:
            return self.response_not_found()
        if i.project != project:
            i.project = project
            i.save()
        return True
