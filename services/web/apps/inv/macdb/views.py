# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.macdb application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import threading
import operator
import re
# Third-party modules
from mongoengine import Q
from django.db.models import Q as d_Q
# NOC modules
from noc.lib.app.extdocapplication import ExtApplication, view
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.macdb import MACDB
from noc.core.cache.decorator import cachedmethod
from cachetools import TTLCache, cachedmethod
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.mac import MAC
from noc.inv.models.maclog import MACLog
from noc.bi.models.mac import MAC as MACDBC
from noc.inv.models.interface import Interface
from noc.core.translation import ugettext as _

# @todo: REST proxy for backend buffered output(paging support in history)
# @todo: search in field Managed Object/Port/Description

tags_lock = threading.RLock()


class MACApplication(ExtApplication):
    """
    MAC application
    """
    title = _("MacDB")
    menu = _("Mac DB")
    model = MACDB
    bi_c = ""
    macdb = MACDBC()
    mac_search_re = re.compile(r"([\dABCDEF][\dABCDEF]:){2,}", re.IGNORECASE)
    mac_search_re_inv = re.compile(r"(:[\dABCDEF][\dABCDEF]){2,}", re.IGNORECASE)

    # query_fields = ["mac"]
    # query_condition = "icontains"
    # int_query_fields = ["vlan"]

    # implied_permissions = {
    #     "read": ["inv:macdb:lookup", "main:style:lookup"]
    # }

    @staticmethod
    def field_description(o, iname):
        # @todo cache
        iface = Interface.objects.filter(managed_object=o, name=iname)
        if not iface:
            iface = ":%s" % iname
        else:
            iface = iface[0]
        return iface

    def api_macdb(self, query, limit=0, offset=0):
        current = []
        m = self.macdb.mac_filter(query, limit=int(limit), offset=int(offset))

        for p in m:
            # mo = self.managedobject_name_to_id(int(p["managed_object"]))
            mo = ManagedObject.objects.filter(bi_id=int(p["managed_object"]))
            if not mo:
                self.logger.warning("Managed object does not exists: %s" % p["managed_object"])
                continue
            mo = mo[0]
            iface = self.field_description(mo, p["interface"])
            current += [{
                "last_changed": p["timestamp"],
                "mac": str(MAC(int(p["mac"]))),
                "vc_domain": str(mo.vc_domain),
                "vc_domain__label": getattr(mo.vc_domain, "name", ""),
                "vlan": p["vlan"],
                "managed_object": str(mo),
                "managed_object__label": str(mo),
                "interface": str(iface),
                "interface__label": str(iface),
                "description": getattr(iface, "description", "")
            }]
        total = len(current)
        if total == int(limit):
            total = int(offset) + int(limit) * 2
        else:
            total = int(offset) + len(current)
        return {"total": total,
                "success": True,
                "data": current}

    @view(method=["GET", "POST"], url="^$", access="read", api=True)
    def api_list(self, request):
        q = dict((str(k), v[0] if len(v) == 1 else v)
                 for k, v in request.GET.lists())
        # find mac request select max(ts), managed_object, interface, vlan from mac
        # where like(MACNumToString(mac), 'A0:AB:1B%') group by managed_object, interface, vlan;
        query = q.get("__query")
        start = q.get("__start")
        limit = q.get("__limit")
        page = q.get("__page")
        out = []
        if not query:
            return self.response(out, status=self.OK)
        try:
            mac = int(MAC(MACAddressParameter(accept_bin=False).clean(query)))
            out = self.api_macdb({"mac": mac}, limit=limit, offset=start)
        except ValueError:
            if self.mac_search_re.match(query):
                out = self.api_macdb({"mac__like": "%s%%" % str(query.upper())}, limit=limit, offset=start)
            elif self.mac_search_re_inv.match(query):
                out = self.api_macdb({"mac__like": "%%%s" % str(query.upper())}, limit=limit, offset=start)
            else:
                # Try MO search
                # @todo ManagedObject search
                self.logger.debug("MACDB ManagedObject search")
                mo_q = ManagedObject.get_search_Q(query)
                if not mo_q:
                    mo_q = d_Q(name__contains=query)
                mos = [mo.get_bi_id() for mo in ManagedObject.objects.filter(mo_q)[:2]]
                if mos:
                    out = self.api_macdb({"managed_object__in": mos}, limit=limit, offset=start)
        # out = self.api_get_maclog(request, mac)
        return self.response(out, status=self.OK)

    @view(url="^(?P<mac>[0-9A-F:]+)/$", method=["GET"],
          access="view", api=True)
    def api_get_maclog(self, request, mac):
        """
        GET maclog
        :param mac:
        :return:
        """

        current = []
        mc = self.macdb
        mac = MAC(mac)
        m = mc.get_mac_history(int(mac))
        # m = MACDB.objects.filter(mac=mac).order_by("-timestamp")
        for p in m:
            # mo = self.managedobject_name_to_id(int(p["managed_object"]))
            # mo = self.bi_c[p["managed_object"]]
            mo = ManagedObject.objects.filter(bi_id=int(p["managed_object"]))
            if not mo:
                self.logger.warning("Managed object does not exists: %s" % p["managed_object"])
                continue
            mo = mo[0]
            iface = Interface.objects.filter(managed_object=mo, name=p["interface"])
            if not iface:
                iface = ":%s" % p["interface"]
            else:
                iface = iface[0]
            current += [{
                "last_changed": p["timestamp"],
                "mac": str(MAC(int(p["mac"]))),
                "vc_domain": str(mo.vc_domain),
                "vc_domain__label": mo.vc_domain.name,
                "vlan": p["vlan"],
                "managed_object": str(mo),
                "managed_object__label": str(mo),
                "interface": str(iface),
                "interface__label": str(iface),
                "description": getattr(iface, "description", "")
            }]

        """
        for p in m:
            if p:
                vc_d = str(p.vc_domain.name) if p.vc_domain else None

                for i in Interface.objects.filter(id=p.interface.id):
                    if i.description:
                        descr = i.description
                    else:
                        descr = None

                current = [{
                    "timestamp": str(p.last_changed),
                    "mac": p.mac,
                    "vc_domain": vc_d,
                    "vlan": p.vlan,
                    "managed_object_name": str(p.managed_object.name),
                    "interface_name": str(p.interface.name),
                    "description": descr
                }]
        """
        history = []
        id_cache = {}
        d_cache = {}

        for i in MACLog.objects.filter(mac=mac).order_by("-timestamp"):
            id = id_cache.get(i.managed_object_name)
            if id is None:        
                for p in ManagedObject.objects.filter(name=i.managed_object_name):
                    id = p.id
                    id_cache[i.managed_object_name] = p.id
            c = d_cache.get((id, i.interface_name))
            if c is None:
                for d in Interface.objects.filter(managed_object=id, name=i.interface_name):
                    if d:
                        if d.description:
                            c = d.description
                            d_cache[id, i.interface_name] = d.description
                        else:
                            c = ""
                            d_cache[id, i.interface_name] = ""

                    else:
                        c = ""
                        d_cache[id, i.interface_name] = ""

            history += [{
                    "timestamp": str(i.timestamp),
                    "mac": i.mac,
                    "vc_domain": str(i.vc_domain_name),
                    "vlan": i.vlan,
                    "managed_object_name": str(i.managed_object_name),
                    "interface_name": str(i.interface_name),
                    "description": c
            }]
        return current
