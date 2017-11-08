# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Template model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import operator
# Python modules
from threading import Lock

import cachetools
import jinja2
# Third-party modules
from django.db import models

id_lock = Lock()


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

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        try:
            return Template.objects.get(id=id)
        except Template.DoesNotExist:
            return None

    def render_subject(self, LANG=None, **kwargs):
        return jinja2.Template(self.subject).render(**kwargs)

    def render_body(self, LANG=None, **kwargs):
        return jinja2.Template(self.body).render(**kwargs)
