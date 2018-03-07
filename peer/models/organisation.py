# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Organisation model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from django.db import models
# NOC modules
from .maintainer import Maintainer


ORG_TYPE_CHOICES = [
    (x, x) for x in ("IANA", "RIR", "NIR", "LIR", "OTHER")
]


class Organisation(models.Model):
    class Meta(object):
        verbose_name = "Organisation"
        verbose_name_plural = "Organisations"
        db_table = "peer_organisation"
        app_label = "peer"

    # NIC Handle
    organisation = models.CharField(
        "Organisation",
        max_length=128, unique=True)
    # org-name:
    org_name = models.CharField("Org. Name", max_length=128)
    # org-type
    org_type = models.CharField(
        "Org. Type",
        max_length=64,
        choices=ORG_TYPE_CHOICES)
    # address: will be prepended automatically for each line
    address = models.TextField("Address")
    # mnt-ref
    mnt_ref = models.ForeignKey(Maintainer, verbose_name="Mnt. Ref")

    def __unicode__(self):
        return u" %s (%s)" % (self.organisation, self.org_name)
