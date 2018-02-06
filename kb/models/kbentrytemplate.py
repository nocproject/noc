# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# KBEntryTemplate model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import re
# Third-party modules
from django.db import models
# NOC modules
from noc.lib.app.site import site
from noc.core.model.fields import AutoCompleteTagsField
from noc.main.models.language import Language
from .kbentry import parser_registry  # Load


class KBEntryTemplate(models.Model):
    """
    KB Entry Template
    """
    class Meta:
        verbose_name = "KB Entry Template"
        verbose_name_plural = "KB Entry Templates"
        app_label = "kb"
        db_table = "kb_kbentrytemplate"
        ordering = ("id",)

    name = models.CharField("Name", max_length=128, unique=True)
    subject = models.CharField("Subject", max_length=256)
    body = models.TextField("Body")
    language = models.ForeignKey(Language, verbose_name="Language",
                                 limit_choices_to={"is_active": True})
    markup_language = models.CharField("Markup Language", max_length="16",
                                       choices=parser_registry.choices)
    tags = AutoCompleteTagsField("Tags", null=True, blank=True)

    rx_template_var = re.compile("{{([^}]+)}}", re.MULTILINE)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return site.reverse("kb:kbentrytemplate:change", self.id)

    @property
    def _var_list(self):
        """
        Returns template variables list
        """
        var_set = set(self.rx_template_var.findall(self.subject))
        var_set.update(self.rx_template_var.findall(self.body))
        return sorted(var_set)
