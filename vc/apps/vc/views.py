# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## vc.vc application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.vc.models import VC, VCDomain, VCFilter
from noc.inv.models import SubInterface, Q
from noc.sa.interfaces import DictParameter, ModelParameter, ListOfParameter,\
    IntParameter, StringParameter
from noc.sa.caches import managedobjectselector_object_ids
from noc.vc.caches import vcinterfacescount, vcprefixes


class VCApplication(ExtModelApplication):
    """
    VC application
    """
    title = "VC"
    menu = "Virtual Circuits"
    model = VC
    icon = "icon_link"

    query_fields = ["name", "description"]
    query_condition = "icontains"
    int_query_fields = ["l1", "l2"]

    implied_permissions = {
        "read": ["vc:vcdomain:lookup", "main:style:lookup"]
    }

    mrt_config = {
        "get_vlans": {
            "map_script": "get_vlans",
            "timeout": 120,
            "access": "import"
        },
        "set_switchport": {
            "map_script": "set_switchport",
            "timeout": 120,
            "access": "set_untagged"
        }
    }

    def get_vc_domain_objects(self, vc_domain):
        return vc_domain.managedobject_set.all()

    def lookup_vcfilter(self, q, name, value):
        """
        Resolve __vcflter lookups
        :param q:
        :param name:
        :param value:
        :return:
        """
        value = ModelParameter(VCFilter).clean(value)
        x = value.to_sql(name)
        try:
            q[None] += [x]
        except KeyError:
            q[None] = [x]

    def field_interfaces_count(self, obj):
        n = vcinterfacescount.get(obj)
        return str(n) if n else "-"

    def field_prefixes(self, obj):
        p = vcprefixes.get(obj)
        if p:
            return ", ".join(p)
        else:
            return "-"

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""

    @view(url="^find_free/$", method=["GET"], access="read", api=True,
          validate={
              "vc_domain": ModelParameter(VCDomain),
              "vc_filter": ModelParameter(VCFilter)
          })
    def api_find_free(self, request, vc_domain, vc_filter, **kwargs):
        return vc_domain.get_free_label(vc_filter)

    @view(url="^bulk/import/", method=["POST"], access="import", api=True,
          validate={
              "vc_domain": ModelParameter(VCDomain),
              "items": ListOfParameter(element=DictParameter(attrs={
                  "l1": IntParameter(),
                  "l2": IntParameter(),
                  "name": StringParameter(),
                  "description": StringParameter(default="")
              }))
          })
    def api_bulk_import(self, request, vc_domain, items):
        n = 0
        for i in items:
            if not VC.objects.filter(vc_domain=vc_domain,
                                     l1=i["l1"], l2=i["l2"]).exists():
                # Add only not-existing
                VC(vc_domain=vc_domain, l1=i["l1"], l2=i["l2"],
                   name=i["name"], description=i["description"]).save()
                n += 1
        return {
            "status": True,
            "imported": n
        }

    @view(url=r"^(?P<vc_id>\d+)/interfaces/$", method=["GET"],
          access="read", api=True)
    def api_interfaces(self, request, vc_id):
        """
        Returns a dict of {untagged: ..., tagged: ...., l3: ...}
        :param request:
        :param vc_id:
        :return:
        """
        vc = self.get_object_or_404(VC, id=int(vc_id))
        l1 = vc.l1
        # Managed objects in VC domain
        objects = set(vc.vc_domain.managedobject_set.values_list(
            "id", flat=True))
        # Find untagged interfaces
        si_objects = defaultdict(list)
        for si in SubInterface.objects.filter(
            managed_object__in=objects,
            untagged_vlan=l1,
            enabled_afi="BRIDGE"):
            si_objects[si.managed_object] += [{"name": si.name}]
        untagged = [{
            "managed_object_id": o.id,
            "managed_object_name": o.name,
            "interfaces": sorted(si_objects[o], key=lambda x: x["name"])
        } for o in si_objects]
        # Find tagged interfaces
        si_objects = defaultdict(list)
        for si in SubInterface.objects.filter(
            managed_object__in=objects,
            tagged_vlans=l1,
            enabled_afi="BRIDGE"):
            si_objects[si.managed_object] += [{"name": si.name}]
        tagged = [{
            "managed_object_id": o.id,
            "managed_object_name": o.name,
            "interfaces": sorted(si_objects[o], key=lambda x: x["name"])
        } for o in si_objects]
        # Find l3 interfaces
        si_objects = defaultdict(list)
        for si in SubInterface.objects.filter(
            managed_object__in=objects,
            vlan_ids=l1):
            si_objects[si.managed_object] += [{
                "name": si.name,
                "ipv4_addresses": si.ipv4_addresses,
                "ipv6_addresses": si.ipv6_addresses
            }]
        l3 = [{"managed_object_id": o.id,
               "managed_object_name": o.name,
               "interfaces": sorted(si_objects[o], key=lambda x: x["name"])
        } for o in si_objects]
        # Update caches
        ic = sum(len(x["interfaces"]) for x in untagged)
        ic += sum(len(x["interfaces"]) for x in tagged)
        ic += sum(len(x["interfaces"]) for x in l3)
        vcinterfacescount.set(ic, vc)
        #
        return {
            "untagged": sorted(untagged,
                               key=lambda x: x["managed_object_name"]),
            "tagged": sorted(tagged, key=lambda x: x["managed_object_name"]),
            "l3": sorted(l3, key=lambda x: x["managed_object_name"])
        }
