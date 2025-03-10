# ---------------------------------------------------------------------
# sa.serviceinstance application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.queryset import Q

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.serviceinstance import ServiceInstance, AddressItem
from noc.sa.models.managedobject import ManagedObject
from noc.core.validators import is_ipv4, is_mac
from noc.core.translation import ugettext as _


class ServiceInstanceApplication(ExtDocApplication):
    """
    sa.serviceinstance application
    """

    title = _("Service Instances")
    menu = _("Service Instances")
    model = ServiceInstance
    query_fields = ["name__contains", "fqdn__contains"]

    def field_label(self, o):
        return str(o)

    def field_service_label(self, o):
        return str(o.service)

    def bulk_field_managed_object(self, data):
        """
        Apply interface_count fields
        :param data:
        :return:
        """
        mos_ids = [x["managed_object"] for x in data]
        if not mos_ids:
            return data
        mos = dict(ManagedObject.objects.filter(id__in=mos_ids).values_list("id", "name"))
        # Apply service instance
        for x in data:
            x["managed_object"] = mos.get(x["managed_object"], x["managed_object"])
        return data

    def instance_to_dict(self, o, fields=None, nocustom=False):
        if isinstance(o, AddressItem):
            return o.address
        data = super().instance_to_dict(o, fields, nocustom)
        return data

    def get_Q(self, request, query):
        if is_ipv4(query.strip()):
            q = Q(addresses__address=query.strip())
        elif is_mac(query.strip()):
            q = Q(macs=[query.strip()])
        else:
            q = super().get_Q(request, query)
        return q
