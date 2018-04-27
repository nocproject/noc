# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Template model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
# Third-party modules
from django.db import models
from django.core.exceptions import ValidationError
import jinja2
import cachetools
# NOC modules
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


def template_validator(value):
    if not value:
        return
    try:
        jinja2.Template(value)
    except jinja2.exceptions.TemplateSyntaxError as e:
        raise ValidationError(str(e))


@on_delete_check(check=[
    ("ip.AddressProfile", "name_template"),
    ("ip.AddressProfile", "fqdn_template"),
    ("ip.PrefixProfile", "name_template"),
    ("vc.VPNProfile", "name_template")
])
class Template(models.Model):
    class Meta:
        app_label = "main"
        db_table = "main_template"
        verbose_name = "Template"
        verbose_name_plural = "Templates"
        ordering = ["name"]

    name = models.CharField("Name", unique=True, max_length=128)
    subject = models.TextField("Subject", validators=[template_validator])
    body = models.TextField("Body", validators=[template_validator])

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        t = Template.objects.filter(id=id)[:1]
        if t:
            return t[0]
        return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        t = Template.objects.filter(name=name)[:1]
        if t:
            return t[0]
        return None

    def render_subject(self, LANG=None, **kwargs):
        return jinja2.Template(self.subject).render(**kwargs)

    def render_body(self, LANG=None, **kwargs):
        return jinja2.Template(self.body).render(**kwargs)
