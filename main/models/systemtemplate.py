# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Template model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from django.db import models
from django.contrib.auth.models import User
import six
# NOC modules
from .template import Template


class SystemTemplate(models.Model):
    class Meta(object):
        app_label = "main"
        db_table = "main_systemtemplate"
        verbose_name = "System template"
        verbose_name_plural = "System templates"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    description = models.TextField("Description", null=True, blank=True)
    template = models.ForeignKey(Template, verbose_name="Template")

    def __unicode__(self):
        return self.name

    def render_subject(self, LANG=None, **kwargs):
        return self.template.render_subject(lang=LANG, **kwargs)

    def render_body(self, LANG=None, **kwargs):
        return self.template.render_body(lang=LANG, **kwargs)

    @classmethod
    def notify_users(cls, name, users, **kwargs):
        """
        Send notifications via template to users
        :param name: System template name
        :param users: List of User instances or id's
        """
        # Find system template by name
        try:
            t = cls.objects.get(name=name)  # noqa
        except cls.DoesNotExist:
            return
        # Fix users
        u_list = []
        for u in users:
            if isinstance(u, six.integer_types):
                try:
                    u_list += [User.objects.get(id=u)]
                except User.DoesNotExist:
                    continue
            elif isinstance(u, six.string_types):
                u_list += [User.objects.get(username=u)]
            elif isinstance(u, User):
                u_list += [u]
        # Left only active users
        u_list = [u for u in u_list if u.is_active]  # noqa
        # Send notifications
        # @todo: Really send notification
