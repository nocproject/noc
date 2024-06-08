# ---------------------------------------------------------------------
# sa.objectlist application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db.models import Q as d_Q

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.capability import Capability
from noc.sa.interfaces.base import ListOfParameter, IPv4Parameter, DictParameter
from noc.sa.models.useraccess import UserAccess

JP_CLAUSE_PATTERN = "jsonb_path_exists(caps, '$[*] ? (@.capability == \"{}\") ? (@.value {} {})')"


class ObjectListApplication(ExtApplication):
    """
    ManagedObject application
    """

    model = ManagedObject
    # Default filter by is_managed
    managed_filter = True

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        self.logger.info("Queryset %s" % query)
        if self.managed_filter:
            q = d_Q(is_managed=True)
        else:
            q = d_Q()
        if not request.user.is_superuser:
            q &= UserAccess.Q(request.user)
        if query:
            sq = ManagedObject.get_search_Q(query)
            if sq:
                q &= sq
            else:
                q &= d_Q(name__contains=query)
        nq = {}
        if request.method == "POST":
            if self.site.is_json(request.META.get("CONTENT_TYPE")):
                nq = self.deserialize(request.body)
            else:
                nq = {str(k): v[0] if len(v) == 1 else v for k, v in request.POST.lists()}
        else:
            nq = {str(k): v[0] if len(v) == 1 else v for k, v in request.GET.lists()}

        jp_clauses = []
        for cc in [part for part in nq if part.startswith("caps")]:
            """
            Caps: caps0=CapsID,caps1=CapsID:true....
            cq - caps query
            mq - main_query
            caps0=CapsID - caps is exists
            caps0=!CapsID - caps is not exists
            caps0=CapsID:true - caps value equal True
            caps0=CapsID:2~50 - caps value many then 2 and less then 50
            """

            c = nq.pop(cc)
            if not c:
                continue

            self.logger.info("[%s] Caps", c)
            if "!" in c:
                # @todo Добавить исключение (только этот) !ID
                c_id = c[1:]
                c_query = "nexists"
            elif ":" not in c:
                c_id = c
                c_query = "exists"
            else:
                c_id, c_query = c.split(":", 1)
            caps = Capability.get_by_id(c_id)
            self.logger.info("[%s] Caps: %s", c, caps)

            if "~" in c_query:
                l, r = c_query.split("~")
                if not l:
                    jp_clauses.append(JP_CLAUSE_PATTERN.format(caps.id, "<=", r))
                elif not r:
                    jp_clauses.append(JP_CLAUSE_PATTERN.format(caps.id, ">=", l))
                else:
                    # TODO This functionality is not implemented in frontend
                    jp_clauses.append(JP_CLAUSE_PATTERN.format(caps.id, "<=", r))
                    jp_clauses.append(JP_CLAUSE_PATTERN.format(caps.id, ">=", l))
            elif c_query in ("false", "true"):
                q &= d_Q(caps__contains=[{"capability": str(caps.id), "value": c_query == "true"}])
            elif c_query == "exists":
                q &= d_Q(caps__contains=[{"capability": str(caps.id)}])
                continue
            elif c_query == "nexists":
                q &= ~d_Q(caps__contains=[{"capability": str(caps.id)}])
                continue
            else:
                value = caps.clean_value(c_query)
                q &= d_Q(caps__contains=[{"capability": str(caps.id), "value": value}])

        queryset = self.model.objects.filter(q)
        if jp_clauses:
            queryset = queryset.extra(where=jp_clauses)
        return queryset

    def instance_to_dict(self, o, fields=None):
        return {
            "id": str(o.id),
            "name": o.name,
            "address": o.address,
            "profile_name": o.profile.name,
            "platform": o.platform.name if o.platform else "",
            "version": o.version.version if o.version else "",
            "row_class": o.object_profile.style.css_class_name if o.object_profile.style else "",
            # "row_class": ""
        }

    def cleaned_query(self, q):
        nq = {}
        for k in q:
            if not k.startswith("_") and "__" not in k:
                nq[k] = q[k]
        self.logger.debug("Cleaned query: %s" % nq)
        if "ids" in nq:
            nq["id__in"] = list({int(nid) for nid in nq["ids"]})
            del nq["ids"]

        if "administrative_domain" in nq:
            ad = AdministrativeDomain.get_nested_ids(int(nq["administrative_domain"]))
            if ad:
                del nq["administrative_domain"]
                nq["administrative_domain__in"] = ad
        if "resource_group" in q:
            rgs = self.get_object_or_404(ResourceGroup, id=q["resource_group"])
            nq["effective_service_groups__overlap"] = ResourceGroup.get_nested_ids(rgs)
            del nq["resource_group"]
        if "addresses" in nq:
            if isinstance(nq["addresses"], list):
                nq["address__in"] = nq["addresses"]
            else:
                nq["address__in"] = [nq["addresses"]]
            del nq["addresses"]

        xf = list((set(nq.keys())) - set(f.name for f in self.model._meta.get_fields()))
        for x in xf:
            if x in ["address__in", "id__in", "administrative_domain__in"]:
                continue
            self.logger.warning("Remove element not in model: %s" % x)
            del nq[x]
        return nq

    def extra_query(self, q, order):
        extra = {"select": {}}
        if "address" in order:
            extra["select"]["ex_address"] = " cast_test_to_inet(address) "
            extra["order_by"] = ["ex_address", "address"]
        elif "-address" in order:
            extra["select"]["ex_address"] = " cast_test_to_inet(address) "
            extra["order_by"] = ["-ex_address", "-address"]

        self.logger.info("Extra: %s" % extra)
        return extra, [] if "order_by" in extra else order

    @view(method=["GET", "POST"], url="^$", access="read", api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict)

    @view(
        method=["POST"],
        url="^iplist/$",
        access="launch",
        api=True,
        validate={
            "query": DictParameter(
                attrs={"addresses": ListOfParameter(element=IPv4Parameter(), convert=True)}
            )
        },
    )
    def api_action_ip_list(self, request, query):
        # @todo Required user vault implementation
        return self.render_json({"status": True})
