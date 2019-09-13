# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.interface application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine import Q

# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.sa.models.managedobject import ManagedObject
from noc.services.web.apps.sa.objectlist.views import ObjectListApplication
from noc.sa.models.useraccess import UserAccess
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.sa.interfaces.base import (
    StringParameter,
    ListOfParameter,
    DocumentParameter,
    ModelParameter,
)
from noc.main.models.resourcestate import ResourceState
from noc.project.models.project import Project
from noc.vc.models.vcdomain import VCDomain
from noc.lib.text import split_alnum
from noc.core.translation import ugettext as _
from noc.config import config


class InterfaceAppplication(ExtApplication):
    """
    inv.interface application
    """

    title = _("Interfaces")
    menu = _("Interfaces")

    mrt_config = {
        "get_mac": {
            "map_script": "get_mac_address_table",
            "timeout": config.script.timeout,
            "access": "get_mac",
        }
    }

    def __init__(self, *args, **kwargs):
        super(InterfaceAppplication, self).__init__(*args, **kwargs)
        self.style_cache = {}  # profile_id -> css_style
        self.default_state = ResourceState.get_default()

    # helpers
    def get_style(self, i):
        profile = i.profile
        if profile:
            try:
                return self.style_cache[profile.id]
            except KeyError:
                pass
            if profile.style:
                s = profile.style.css_class_name
            else:
                s = ""
            self.style_cache[profile.id] = s
            return s
        else:
            return ""

    @staticmethod
    def sorted_iname(s):
        return sorted(s, key=lambda x: split_alnum(x["name"]))

    @staticmethod
    def get_link(i):
        link = i.link
        if not link:
            return None
        if link.is_ptp:
            # ptp
            o = link.other_ptp(i)
            label = "%s:%s" % (o.managed_object.name, o.name)
        elif link.is_lag:
            # unresolved LAG
            o = [ii for ii in link.other(i) if ii.managed_object.id != i.managed_object.id]
            label = "LAG %s: %s" % (o[0].managed_object.name, ", ".join(ii.name for ii in o))
        else:
            # Broadcast
            label = ", ".join("%s:%s" % (ii.managed_object.name, ii.name) for ii in link.other(i))
        return {"id": str(link.id), "label": label}

    @staticmethod
    def convert_mo_interface_url(o_id):
        return "#sa.managedobject/%s/interfaces" % o_id

    def prepare_l1_iface_data(self, i, o):
        """
        :param i:  interface object
        :param o: managed_object
        :return: dict with data of attributes
        """
        return {
            "id": str(i.id),
            "name": i.name,
            "description": i.description,
            "mac": i.mac,
            "ifindex": i.ifindex,
            "lag": (i.aggregated_interface.name if i.aggregated_interface else ""),
            "link": self.get_link(i),
            "profile": str(i.profile.id) if i.profile else None,
            "profile__label": unicode(i.profile) if i.profile else None,
            "enabled_protocols": i.enabled_protocols,
            "project": i.project.id if i.project else None,
            "project__label": unicode(i.project) if i.project else None,
            "state": i.state.id if i.state else self.default_state.id,
            "state__label": unicode(i.state if i.state else self.default_state),
            "vc_domain": i.vc_domain.id if i.vc_domain else None,
            "vc_domain__label": unicode(i.vc_domain) if i.vc_domain else None,
            "row_class": self.get_style(i),
            "mo": o.name,
            "url": self.convert_mo_interface_url(o.id),
        }

    def prepare_lag_iface_data(self, i, o):
        """
        :param i:  interface object
        :param o: managed_object
        :return: dict with data of attributes
        """
        return {
            "id": str(i.id),
            "name": i.name,
            "description": i.description,
            "members": [
                j.name
                for j in Interface.objects.filter(managed_object=o.id, aggregated_interface=i.id)
            ],
            "profile": str(i.profile.id) if i.profile else None,
            "profile__label": unicode(i.profile) if i.profile else None,
            "enabled_protocols": i.enabled_protocols,
            "project": i.project.id if i.project else None,
            "project__label": unicode(i.project) if i.project else None,
            "state": i.state.id if i.state else self.default_state.id,
            "state__label": unicode(i.state if i.state else self.default_state),
            "vc_domain": i.vc_domain.id if i.vc_domain else None,
            "vc_domain__label": unicode(i.vc_domain) if i.vc_domain else None,
            "row_class": self.get_style(i),
            "mo": o.name,
            "url": self.convert_mo_interface_url(o.id),
        }

    def prepare_l2_iface_data(self, i, o):
        """
        :param i:  interface object
        :param o: managed_object
        :return: dict with data of attributes
        """
        return {
            "name": i.name,
            "description": i.description,
            "untagged_vlan": i.untagged_vlan,
            "tagged_vlans": i.tagged_vlans,
            "mo": o.name,
            "url": self.convert_mo_interface_url(o.id),
        }

    def prepare_l3_iface_data(self, i, o):
        """
        :param i:  interface object
        :param o: managed_object
        :return: dict with data of attributes
        """
        return {
            "name": i.name,
            "description": i.description,
            "ipv4_addresses": i.ipv4_addresses,
            "ipv6_addresses": i.ipv6_addresses,
            "enabled_protocols": i.enabled_protocols,
            "vlan": i.vlan_ids,
            "vrf": i.forwarding_instance.name if i.forwarding_instance else "",
            "mo": o.name,
            "url": self.convert_mo_interface_url(o.id),
        }

    @staticmethod
    def qdict_to_dict(qdict):
        """Convert a Django QueryDict to a Python dict.

        Single-value fields are put in directly, and for multi-value fields, a list
        of all values is stored at the field's key.

        """
        return {k: v[0] if len(v) == 1 else v for k, v in qdict.lists()}

    # api
    @view(url="^(?P<managed_object>\d+)/$", method=["GET"], access="view", api=True)
    def api_get_interfaces(self, request, managed_object):
        """
        GET interfaces
        :param managed_object:
        :return:
        """
        # Get object
        o = self.get_object_or_404(ManagedObject, id=int(managed_object))
        if not o.has_access(request.user):
            return self.response_forbidden("Permission denied")
        # Physical interfaces
        # @todo: proper ordering
        l1 = [
            self.prepare_l1_iface_data(i, o)
            for i in Interface.objects.filter(managed_object=o.id, type="physical")
        ]
        # LAG
        lag = [
            self.prepare_lag_iface_data(i, o)
            for i in Interface.objects.filter(managed_object=o.id, type="aggregated")
        ]
        # L2 interfaces
        l2 = [
            self.prepare_l2_iface_data(i, o)
            for i in SubInterface.objects.filter(managed_object=o.id, enabled_afi="BRIDGE")
        ]
        # L3 interfaces
        q = Q(enabled_afi="IPv4") | Q(enabled_afi="IPv6")
        l3 = [
            self.prepare_l3_iface_data(i, o)
            for i in SubInterface.objects.filter(managed_object=o.id).filter(q)
        ]
        return {
            "l1": self.sorted_iname(l1),
            "lag": self.sorted_iname(lag),
            "l2": self.sorted_iname(l2),
            "l3": self.sorted_iname(l3),
        }

    @view(
        url="^link/$",
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

    @view(url="^unlink/(?P<iface_id>[0-9a-f]{24})/$", method=["POST"], access="link", api=True)
    def api_unlink(self, request, iface_id):
        i = Interface.objects.filter(id=iface_id).first()
        if not i:
            return self.response_not_found()
        try:
            i.unlink()
            return {"status": True, "msg": "Unlinked"}
        except ValueError as why:
            return {"status": False, "msg": str(why)}

    @view(url="^unlinked/(?P<object_id>\d+)/$", method=["GET"], access="link", api=True)
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
        return sorted(r, key=lambda x: split_alnum(x["label"]))

    @view(
        url="^l1/(?P<iface_id>[0-9a-f]{24})/change_profile/$",
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
        url="^l1/(?P<iface_id>[0-9a-f]{24})/change_state/$",
        validate={"state": ModelParameter(ResourceState)},
        method=["POST"],
        access="profile",
        api=True,
    )
    def api_change_state(self, request, iface_id, state):
        i = Interface.objects.filter(id=iface_id).first()
        if not i:
            return self.response_not_found()
        if i.state != state:
            i.state = state
            i.save()
        return True

    @view(
        url="^l1/(?P<iface_id>[0-9a-f]{24})/change_project/$",
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

    @view(
        url="^l1/(?P<iface_id>[0-9a-f]{24})/change_vc_domain/$",
        validate={"vc_domain": ModelParameter(VCDomain, required=False)},
        method=["POST"],
        access="profile",
        api=True,
    )
    def api_change_vc_domain(self, request, iface_id, vc_domain):
        i = Interface.objects.filter(id=iface_id).first()
        if not i:
            return self.response_not_found()
        if i.vc_domain != vc_domain:
            i.vc_domain = vc_domain
            i.save()
        return True

    @view(url="^search_description/(?P<description>.*?)/$", method=["GET"], access="view", api=True)
    def api_search_description(self, request, description):
        """
        GET interfaces by description
        :param request:
        :param description:
        :return:
        """
        params = self.qdict_to_dict(request.GET)
        mos = ManagedObject.objects.all()
        if params and "is_managed" in params:
            if not params.get("is_managed") == "all":
                is_managed = params.get("is_managed") == "true"
                mos = mos.filter(is_managed=is_managed)
            del params["is_managed"]
        if params:
            q = ObjectListApplication.cleaned_query(
                ObjectListApplication(ObjectListApplication), params
            )
            if q:
                mos = mos.filter(**q)
        if "__query" in params.keys():
            mos = mos.filter(name__icontains=params["__query"])
        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        l1 = (
            []
            if len(description) < 2
            else [
                self.prepare_l1_iface_data(i, i.managed_object)
                for i in Interface.objects.filter(
                    description__icontains=description, type="physical", managed_object__in=mos
                )[:300]
            ]
        )
        # LAG
        lag = (
            []
            if len(description) < 2
            else [
                self.prepare_lag_iface_data(i, i.managed_object)
                for i in Interface.objects.filter(
                    description__icontains=description, type="aggregated", managed_object__in=mos
                )[:300]
            ]
        )
        # L2 interfaces
        l2 = (
            []
            if len(description) < 2
            else [
                self.prepare_l2_iface_data(i, i.managed_object)
                for i in SubInterface.objects.filter(
                    description__icontains=description, enabled_afi="BRIDGE", managed_object__in=mos
                )[:300]
            ]
        )
        # L3 interfaces
        q = Q(enabled_afi="IPv4") | Q(enabled_afi="IPv6")
        l3 = (
            []
            if len(description) < 2
            else [
                self.prepare_l3_iface_data(i, i.managed_object)
                for i in SubInterface.objects.filter(
                    description__icontains=description, managed_object__in=mos
                ).filter(q)[:300]
            ]
        )
        return {
            "l1": self.sorted_iname(l1),
            "lag": self.sorted_iname(lag),
            "l2": self.sorted_iname(l2),
            "l3": self.sorted_iname(l3),
        }
