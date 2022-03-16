# ----------------------------------------------------------------------
# Community Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from .communitytype import CommunityType


class Community(NOCModel):
    class Meta(object):
        verbose_name = "Community"
        verbose_name_plural = "Communities"
        db_table = "peer_community"
        app_label = "peer"

    community = models.CharField("Community", max_length=20, unique=True)
    type = models.ForeignKey(CommunityType, verbose_name="Type", on_delete=models.CASCADE)
    description = models.TextField("Description")

    def __str__(self):
        return self.community
