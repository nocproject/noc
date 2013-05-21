# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Project models
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models


class Project(models.Model):
    """
    Projects are used to track investment projects expenses and profits
    """
    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        app_label = "project"
        db_table = "project_project"

    code = models.CharField("Code", max_length=256, unique=True)
    name = models.CharField("Name", max_length=256)
    description = models.TextField("Description", null=True, blank=True)

    def __unicode__(self):
        return self.code
