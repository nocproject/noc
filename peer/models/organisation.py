# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
=======
##----------------------------------------------------------------------
## Organisation model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## NOC modules
from maintainer import Maintainer
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


ORG_TYPE_CHOICES = [
    (x, x) for x in ("IANA", "RIR", "NIR", "LIR", "OTHER")
]


class Organisation(models.Model):
<<<<<<< HEAD
    class Meta(object):
=======
    class Meta:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
