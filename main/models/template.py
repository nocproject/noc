# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Template model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from django.db import models
from django.template import Template as DjangoTemplate
from django.template import Context


class Template(models.Model):
    class Meta:
        app_label = "main"
        db_table = "main_template"
        verbose_name = "Template"
        verbose_name_plural = "Templates"
        ordering = ["name"]

    name = models.CharField("Name", unique=True, max_length=128)
    subject = models.TextField("Subject")
    body = models.TextField("Body")

    def __unicode__(self):
        return self.name

    def render_subject(self, LANG=None, **kwargs):
        return DjangoTemplate(self.subject).render(Context(kwargs))

    def render_body(self, LANG=None, **kwargs):
        return DjangoTemplate(self.body).render(Context(kwargs))
