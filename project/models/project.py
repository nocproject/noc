# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Project models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
# Third-party modules
from django.db import models
import cachetools
# NOC modules
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@on_delete_check(check=[
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
    ("vc.VC", "project")
])
class Project(models.Model):
    """
    Projects are used to track investment projects expenses and profits
    """
    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        app_label = "project"
        db_table = "project_project"

    code = models.CharField("Code", max_length=256, unique=True)
    name = models.CharField("Name", max_length=256)
    description = models.TextField("Description", null=True, blank=True)

    _id_cache = cachetools.TTLCache(100, ttl=60)

    def __unicode__(self):
        return self.code

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda x: id_lock)
    def get_by_id(cls, id):
        try:
            return Project.objects.get(id=id)
        except Project.DoesNotExist:
            return None
