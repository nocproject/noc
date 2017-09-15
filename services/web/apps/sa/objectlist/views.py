# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.objectlist application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python module
import itertools
import bson
# Third-party modules
from django.db.models import Q as d_Q
from noc.lib.nosql import Q as m_Q
# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.firmware import Firmware
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.objectcapabilities import ObjectCapabilities
from noc.sa.interfaces.base import (ListOfParameter, IPv4Parameter, DictParameter)
from noc.sa.models.useraccess import UserAccess


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
        return self.model.objects.filter(q)

    def instance_to_dict(self, o, fields=None):
        return {
            "id": str(o.id),
            "name": o.name,
            "address": o.address,
            "profile_name": o.profile.name,
            "platform": o.platform.name if o.platform else "",
            "version": o.version.version if o.version else "",
            "row_class": o.object_profile.style.css_class_name if o.object_profile.style else ""
            # "row_class": ""
        }

    def cleaned_query(self, q):
        nq = {}
        for k in q:
            if not k.startswith("_") and "__" not in k:
                nq[k] = q[k]
        ids = set()
        self.logger.debug("Cleaned query: %s" % nq)
        if "ids" in nq:
            ids = set([int(nid) for nid in nq["ids"]])
            del nq["ids"]

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
                if ids:
                    # nq["id__in"] = set(ManagedObject.objects.filter(s.Q).values_list("id", flat=True))
                    ids = ids.intersection(set(ManagedObject.objects.filter(s.Q).values_list("id", flat=True)))
                else:
                    ids = set(ManagedObject.objects.filter(s.Q).values_list("id", flat=True))
            del nq["selector"]
        mq = None
        c_in = []
        c_nin = []
        for cc in itertools.ifilter(lambda part: part.startswith("caps"), nq.keys()):
            """
            Caps: caps0=CapsID,caps1=CapsID:true....
            cq - caps query
            mq - main_query
            caps0=CapsID - caps is exists
            caps0=!CapsID - caps is not exists
            caps0=CapsID:true - caps value equal True
            caps0=CapsID:2~50 - caps value many then 2 and less then 50
            c_ids = set(ObjectCapabilities.objects(cq).distinct('object'))
            """
            # @todo Убирать дубликаты (повторно не добавлять)

            c = nq.pop(cc)
            if not c:
                continue
            if not mq:
                mq = m_Q()
            self.logger.info("Caps: %s" % c)
            if "!" in c:
                # @todo Добавить исключение (только этот) !ID
                c_id = c[1:]
                c_query = "nexists"
            elif ":" not in c:
                c_id = c
                c_query = "exists"
            else:
                c_id, c_query = c.split(":", 1)

            try:
                c_id = bson.ObjectId(c_id)
            except bson.errors.InvalidId as e:
                self.logger.warning(e)
                continue
            if "~" in c_query:
                l, r = c_query.split("~")
                if not l:
                    cond = {"$lte": int(r)}
                elif not r:
                    cond = {"$gte": int(l)}
                else:
                    cond = {"$lte": int(r), "$gte": int(l)}
                cq = m_Q(__raw__={"caps": {"$elemMatch": {"capability": c_id,
                                                          "value": cond}}})
            elif c_query in ("false", "true"):
                cq = (m_Q(caps__match={"capability": c_id, "value": c_query == "true"}))
            elif c_query == "exists":
                c_in += [c_id]
                continue
            elif c_query == "nexists":
                c_nin += [c_id]
                continue
            else:
                try:
                    c_query = int(c_query)
                    cq = m_Q(__raw__={"caps": {"$elemMatch": {"capability": c_id,
                                                              "value": int(c_query)}}})
                except ValueError:
                    cq = m_Q(__raw__={"caps": {"$elemMatch": {"capability": c_id,
                                                              "value": {"$regex": c_query}}}})
            mq &= cq
        if c_in:
            mq &= m_Q(caps__capability__in=c_in)
        if c_nin:
            mq &= m_Q(caps__capability__nin=c_nin)
        if mq:
            c_ids = set(el["_id"] for el in ObjectCapabilities.objects(mq).values_list('object').as_pymongo())
            self.logger.info("Caps objects count: %d" % len(c_ids))
            ids = ids.intersection(c_ids) if ids else c_ids

        if "addresses" in nq:
            if isinstance(nq["addresses"], list):
                nq["address__in"] = nq["addresses"]
            else:
                nq["address__in"] = [nq["addresses"]]
            del nq["addresses"]
        if ids:
            nq["id__in"] = list(ids)

        xf = list((set(nq.keys())) - set(self.model._meta.get_all_field_names()))
        # @todo move validation fields
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

    @view(method=["POST"], url="^iplist/$",
          access="launch", api=True,
          validate={
              "query": DictParameter(attrs={"addresses": ListOfParameter(element=IPv4Parameter(), convert=True)})})
    def api_action_ip_list(self, request, query):
        # @todo Required user vault implementation
        return self.render_json({"status": True})
