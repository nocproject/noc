# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Community Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from .communitytype import CommunityType


@six.python_2_unicode_compatible
class Community(NOCModel):
    class Meta(object):
        verbose_name = "Community"
        verbose_name_plural = "Communities"
        db_table = "peer_community"
        app_label = "peer"

    community = models.CharField("Community", max_length=20, unique=True)
    type = models.ForeignKey(CommunityType, verbose_name="Type", on_delete=models.CASCADE)
    description = models.CharField("Description", max_length=64)

    def __str__(self):
        return self.community
