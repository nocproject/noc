# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PeerGroup model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_delete_check


@on_delete_check(check=[("peer.Peer", "peer_group")])
@six.python_2_unicode_compatible
class PeerGroup(NOCModel):
    class Meta(object):
        verbose_name = "Peer Group"
        verbose_name_plural = "Peer Groups"
        db_table = "peer_peergroup"
        app_label = "peer"

    name = models.CharField("Name", max_length=32, unique=True)
    description = models.CharField("Description", max_length=64)
    communities = models.CharField("Import Communities", max_length=128, blank=True, null=True)
    max_prefixes = models.IntegerField("Max. Prefixes", default=100)
    local_pref = models.IntegerField("Local Pref", null=True, blank=True)
    import_med = models.IntegerField("Import MED", blank=True, null=True)
    export_med = models.IntegerField("Export MED", blank=True, null=True)

    def __str__(self):
        return self.name
