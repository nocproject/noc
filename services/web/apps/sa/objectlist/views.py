# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.objectlist application
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from django.db.models import Q
## NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess


class ObjectListApplication(ExtApplication):
    """
    ManagedObject application
    """
    model = ManagedObject

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        q = Q(is_managed=True)
        if not request.user.is_superuser:
            q &= UserAccess.Q(request.user)
        if query:
            sq = ManagedObject.get_search_Q(query)
            if sq:
                q &= sq
        return self.model.objects.filter(q)

    def instance_to_dict(self, o, fields=None):
        return {
            "id": str(o.id),
            "name": o.name,
            "address": o.address,
            "profile_name": o.profile_name,
            "platform": o.platform,
            "row_class": o.object_profile.style.css_class_name if o.object_profile.style else ""
        }

    def cleaned_query(self, q):
        nq = {}
        for k in q:
            if not k.startswith("_"):
                nq[k] = q[k]

        if "administrative_domain" in nq:
            ad = AdministrativeDomain.get_nested_ids(
                int(nq["administrative_domain"])
            )
            if ad:
                del nq["administrative_domain"]
                nq["administrative_domain__in"] = ad

        if "selector" in nq:
            s = self.get_object_or_404(ManagedObjectSelector,
                                       id=int(q["selector"]))
            if s:
                nq["id__in"] = list(ManagedObject.objects.filter(s.Q).values_list("id", flat=True))
            del nq["selector"]
        # @todo Filter capabilities(AND)
        if "caps" in nq:
            del nq["caps"]
            pass
        if "addresses" in nq:
            nq["address__in"] = nq["addresses"]
            del nq["addresses"]

        return nq

    @view(method=["GET"], url="^$", access="read", api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict)

    @view(method=["POST"], url="^iplist/$",
          access="launch", api=True,
          validate={
               "query": DictParameter(attrs={"addresses": ListOfParameter(element=IPv4Parameter(), convert=True),
                                             })
           })
    def api_action_ip_list(self, request, query):
        # @todo Required user vault implementation

        return self.render_json({"status": True})
