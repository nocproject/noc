# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Database models for main module
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
# Third-party modules
from django.db import models
# NOC modules
from noc.lib.validators import check_extension, check_mimetype


class MIMEType(models.Model):
    """
    MIME Type mapping
    """
    class Meta:
        app_label = "main"
        db_table = "main_mimetype"
        verbose_name = "MIME Type"
        verbose_name_plural = "MIME Types"
        ordering = ["extension"]

    extension = models.CharField("Extension", max_length=32, unique=True,
                                 validators=[check_extension])
    mime_type = models.CharField("MIME Type", max_length=63,
                                 validators=[check_mimetype])

    def __unicode__(self):
        return u"%s -> %s" % (self.extension, self.mime_type)

    @classmethod
    def get_mime_type(cls, filename):
        """
        Determine MIME type from filename
        """
        r, ext = os.path.splitext(filename)
        try:
            m = MIMEType.objects.get(extension=ext.lower())
            return m.mime_type
        except MIMEType.DoesNotExist:
            return "application/octet-stream"
