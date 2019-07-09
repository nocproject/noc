# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VCBindFilter model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six
from django.db import models, connection

# NOC modules
from noc.core.model.base import NOCModel
from noc.ip.models.afi import AFI_CHOICES
from noc.core.model.fields import CIDRField
from .vcdomain import VCDomain
from .vcfilter import VCFilter
from .vc import VC


@six.python_2_unicode_compatible
class VCBindFilter(NOCModel):
    class Meta(object):
        verbose_name = "VC Bind Filter"
        verbose_name_plural = "VC Bind Filters"
        db_table = "vc_vcbindfilter"
        app_label = "vc"

    vc_domain = models.ForeignKey(VCDomain, verbose_name="VC Domain", on_delete=models.CASCADE)
    vrf = models.ForeignKey("ip.VRF", verbose_name="VRF", on_delete=models.CASCADE)
    afi = models.CharField("Address Family", max_length=1, choices=AFI_CHOICES, default="4")
    prefix = CIDRField("Prefix")
    vc_filter = models.ForeignKey(VCFilter, verbose_name="VC Filter", on_delete=models.CASCADE)

    def __str__(self):
        return "%s %s %s %s" % (self.vc_domain, self.vrf, self.prefix, self.vc_filter)

    @classmethod
    def get_vcs(cls, vrf, afi, prefix):
        """
        Returns queryset with all suitable VCs
        """
        if hasattr(prefix, "prefix"):
            prefix = prefix.prefix
        c = connection.cursor()
        c.execute(
            """
            SELECT v.id,v.l1,vf.id
            FROM
                vc_vcdomain d JOIN vc_vcbindfilter f ON (d.id=f.vc_domain_id)
                JOIN vc_vcfilter vf ON (f.vc_filter_id=vf.id)
                JOIN vc_vc v ON (v.vc_domain_id=d.id)
            WHERE
                    f.vrf_id=%s
                AND f.afi=%s
                AND f.prefix>>=%s
        """,
            [vrf.id, afi, prefix],
        )
        vcs = set()  # vc.id
        F = {}  # id -> filter
        for vc_id, l1, vf_id in c.fetchall():
            try:
                f = F[vf_id]
            except KeyError:
                f = VCFilter.objects.get(id=vf_id)
                F[vf_id] = f
            if f.check(l1):
                vcs.add(vc_id)
        return VC.objects.filter(id__in=vcs).order_by("l1")
