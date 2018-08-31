# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PeerGroup model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.model.decorator import on_delete_check


@on_delete_check(check=[
    ("peer.Peer", "peer_group")
])
class PeerGroup(models.Model):
    class Meta:
        verbose_name = "Peer Group"
        verbose_name_plural = "Peer Groups"
        db_table = "peer_peergroup"
        app_label = "peer"


    name = models.CharField("Name", max_length=32, unique=True)
    description = models.CharField("Description", max_length=64)
    communities = models.CharField(
        "Import Communities", max_length=128, blank=True, null=True)
    max_prefixes = models.IntegerField("Max. Prefixes", default=100)
    local_pref = models.IntegerField(
        "Local Pref", null=True, blank=True)
    import_med = models.IntegerField(
        "Import MED", blank=True, null=True)
    export_med = models.IntegerField(
        "Export MED", blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)
