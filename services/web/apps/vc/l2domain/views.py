# ----------------------------------------------------------------------
# vc.l2domain application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db.models import Count

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.vc.models.l2domain import L2Domain
from noc.services.web.base.decorators.state import state_handler
from noc.sa.models.managedobject import ManagedObject
from noc.core.translation import ugettext as _


@state_handler
class L2DomainApplication(ExtDocApplication):
    """
    L2 Domain application
    """

    title = "L2 Domain"
    menu = [_("L2 Domain")]
    model = L2Domain
    query_fields = ["name", "description"]
    query_condition = "icontains"
    int_query_fields = ["vlan"]

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""

    def bulk_field_count(self, data):
        l2domains = (str(d["id"]) for d in data)
        counts = dict(
            ManagedObject.objects.filter(l2_domain__in=l2domains)
            .values("l2_domain")
            .annotate(cnt=Count("l2_domain"))
            .values_list("l2_domain", "cnt")
        )
        for row in data:
            row["count"] = counts.get(row["id"], 0)
        return data

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        if not nocustom and "pools" in r:
            for x in r["pools"]:
                x["is_persist"] = False
            for x in o.profile.pools:
                xx = self.instance_to_dict(x, nocustom=True)
                xx["is_persist"] = True
                r["pools"] += [xx]
        return r
