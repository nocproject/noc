# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CommunityType Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import six
from django.db import models

# NOC models
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_delete_check


@on_delete_check(check=[("peer.Community", "type")])
@six.python_2_unicode_compatible
class CommunityType(NOCModel):
    class Meta(object):
        verbose_name = "Community Type"
        verbose_name_plural = "Community Types"
        db_table = "peer_communitytype"
        app_label = "peer"

    name = models.CharField("Description", max_length=32, unique=True)

    def __str__(self):
        return self.name
