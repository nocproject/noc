# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Community Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from django.db import models
# NOC modules
from .communitytype import CommunityType


class Community(models.Model):
    class Meta(object):
        verbose_name = "Community"
        verbose_name_plural = "Communities"
        db_table = "peer_community"
        app_label = "peer"

    community = models.CharField("Community", max_length=20, unique=True)
    type = models.ForeignKey(CommunityType, verbose_name="Type")
    description = models.CharField("Description", max_length=64)

    def __unicode__(self):
        return self.community
