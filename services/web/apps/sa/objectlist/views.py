# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.objectlist application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from collections import defaultdict
import itertools
import bson
# Third-party modules
from django.db.models import Q as d_Q
from noc.lib.nosql import Q as m_Q
# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobject import Version
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.objectcapabilities import ObjectCapabilities
from noc.sa.interfaces.base import (ListOfParameter, ModelParameter, IPv4Parameter,
                                    DictParameter, StringListParameter, StringParameter, InterfaceTypeError)
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
            "profile_name": o.profile_name,
            # "platform": o.platform,
            "platform": o.ex_platform,
            "version": o.ex_version,
            "row_class": o.object_profile.style.css_class_name if o.object_profile.style else ""
            # "row_class": ""
        }

    def cleaned_query(self, q):
        nq = {}
        for k in q:
            if not k.startswith("_") and "__" not in k:
                nq[k] = q[k]
        ids = set()
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
                nq["id__in"] = set(ManagedObject.objects.filter(s.Q).values_list("id", flat=True))
            del nq["selector"]
        mq = None
        for cc in itertools.ifilter(lambda x: x.startswith("caps"), nq.keys()):
            """
            Caps: caps0=CapsID,caps1=CapsID:true....
            cq - caps query
            mq - main_query
            c_ids = set(ObjectCapabilities.objects(cq).distinct('object'))
            """
            # @todo Убирать дубликаты (повторно не добавлять)

            c = nq.pop(cc)
            if "!" in c:
                # @todo Добавить исключение (только этот) !ID
                continue
            if not c:
                continue
            if not mq:
                mq = m_Q()
            self.logger.info("Caps: %s" % c)
            if ":" not in c:
                mq &= m_Q(caps__capability=c)
                continue
            c_id, c_query = c.split(":", 1)
            try:
                c_id = bson.ObjectId(c_id)
            except bson.errors.InvalidId, why:
                self.logger.warning(why)
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
            else:
                try:
                    c_query = int(c_query)
                    cq = m_Q(__raw__={"caps": {"$elemMatch": {"capability": c_id,
                                                               "value": int(c_query)}}})
                except ValueError:
                    cq = m_Q(__raw__={"caps": {"$elemMatch": {"capability": c_id,
                                                               "value": {"$regex": c_query}}}})
            mq &= cq
        if mq:
            c_ids = set(el["_id"] for el in ObjectCapabilities.objects(mq).values_list('object').as_pymongo())
            self.logger.info("Caps objects count: %d" % len(c_ids))
            if "id__in" in nq:
                # @todo union IDS
                pass
            else:
                 nq["id__in"] = c_ids
        pass
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
        # Query for MO attributest. Get key - ex_ATTRNAME
        sql = """SELECT value AS platform 
                 FROM sa_managedobjectattribute AS saa 
                 WHERE key=\'%s\' AND saa.managed_object_id=sa_managedobject.id"""
        # Query for filter by attributest
        sql_w = """EXISTS (SELECT managed_object_id 
                           FROM sa_managedobjectattribute 
                           WHERE managed_object_id=sa_managedobject.id AND key=%s AND value LIKE %s)
                           """
        extra = {"select": {}}
        for v in Version._fields:
            # key = "ex_" + v
            extra["select"]["ex_" + v] = sql % v
            if v in order:
                extra["order_by"] = ["ex_" + v]
            elif "-" + v in order:
                extra["order_by"] = ["-ex_" + v]
        if "address" in order:
            extra["select"]["ex_address"] = " cast_test_to_inet(address) "
            extra["order_by"] = ["ex_address", "address"]
        elif "-address" in order:
            extra["select"]["ex_address"] = " cast_test_to_inet(address) "
            extra["order_by"] = ["-ex_address", "-address"]

        e_q = set(q).intersection(set(Version._fields))
        # Extra filter query
        if e_q:
            extra["where"] = []
            extra["params"] = []
            for e in e_q:
                extra["where"].append(sql_w)
                extra["params"] += [e, "%" + q[e] + "%"]
        self.logger.info("Extra: %s" % extra)
        return extra, [] if "order_by" in extra else order

    @view(method=["GET", "POST"], url="^$", access="read", api=True)
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
