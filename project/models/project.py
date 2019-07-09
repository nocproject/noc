# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Project models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock

# Third-party modules
import six
from django.db import models
import cachetools

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@on_delete_check(
    check=[
        ("crm.Subscriber", "project"),
        ("crm.Supplier", "project"),
        ("dns.DNSZone", "project"),
        ("inv.Interface", "project"),
        ("inv.SubInterface", "project"),
        ("ip.Address", "project"),
        ("ip.Prefix", "project"),
        ("ip.VRF", "project"),
        ("peer.AS", "project"),
        ("peer.ASSet", "project"),
        ("peer.Peer", "project"),
        ("phone.PhoneNumber", "project"),
        ("phone.PhoneRange", "project"),
        ("vc.VC", "project"),
        ("vc.VPN", "project"),
        ("vc.VLAN", "project"),
    ]
)
@six.python_2_unicode_compatible
class Project(NOCModel):
    """
    Projects are used to track investment projects expenses and profits
    """

    class Meta(object):
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        app_label = "project"
        db_table = "project_project"

    code = models.CharField("Code", max_length=256, unique=True)
    name = models.CharField("Name", max_length=256)
    description = models.TextField("Description", null=True, blank=True)

    _id_cache = cachetools.TTLCache(100, ttl=60)

    def __str__(self):
        return self.code

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda x: id_lock)
    def get_by_id(cls, id):
        p = Project.objects.filter(id=id)[:1]
        if p:
            return p[0]
        return None
