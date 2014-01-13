# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## spatial_ref_sys wrapper
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models


class SRS(models.Model):
    """
    PostGIS spatial reference system
    """
    class Meta:
        verbose_name = "SRS"
        verbose_name_plural = "SRS"
        db_table = "spatial_ref_sys"

    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256, null=True, blank=True)
    auth_srid = models.IntegerField(null=True, blank=True)
    proj4text = models.CharField(max_length=2048, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.srid)

    @property
    def full_id(self):
        """
        Get full SRS ID in form of <AUTH>:<ID>
        :return:
        :rtype: str
        """
        return "%s:%d" % (self.auth_name, self.auth_srid)
