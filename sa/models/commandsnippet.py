# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CommandSnippet model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import shlex
## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.template import Template, Context
## NOC modules
from noc.main.models import Permission
from managedobjectselector import ManagedObjectSelector
from noc.core.model.fields import TagsField
from noc.lib.app.site import site


class CommandSnippet(models.Model):
    """
    Command snippet
    """
    class Meta:
        verbose_name = _("Command Snippet")
        verbose_name_plural = _("Command Snippets")
        db_table = "sa_commandsnippet"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length = 128, unique = True)
    description = models.TextField(_("Description"))
    snippet = models.TextField(_("Snippet"),
            help_text=_("Code snippet template"))
    change_configuration = models.BooleanField(_("Change configuration"),
            default=False)
    selector = models.ForeignKey(ManagedObjectSelector,
                                 verbose_name=_("Object Selector"))
    is_enabled = models.BooleanField(_("Is Enabled?"), default=True)
    timeout = models.IntegerField(_("Timeout (sec)"), default=60)
    require_confirmation = models.BooleanField(_("Require Confirmation"),
            default=False)
    ignore_cli_errors = models.BooleanField(_("Ignore CLI errors"),
            default=False)
    # Restrict access to snippet if set
    # effective permission name will be sa:runsnippet:<permission_name>
    permission_name = models.CharField(_("Permission Name"), max_length=64,
                                       null=True, blank=True)
    display_in_menu = models.BooleanField(_("Show in menu"), default=False)
    #
    tags = TagsField(_("Tags"), null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return site.reverse("sa:commandsnippet:change", self.id)

    rx_var = re.compile(r"{{\s*([^|}]+?)\s*(?:\|.+?)?}}", re.MULTILINE)
    rx_vartag = re.compile(r"\{%\s*var\s+(?P<name>\S+)\s+(?P<type>\S+)(?P<rest>.*)\s*%\}",
                           re.MULTILINE)

    @property
    def vars(self):
        """
        Variables used in snippet. Returns dict
        name -> {type: , required: }
        """
        vars = {}
        # Search for {{ var }}
        for v in self.rx_var.findall(self.snippet):
            if "." in v:
                v = v.split(".", 1)[0]
            if v != "object":
                vars[v] = {
                    "type": "str",
                    "required": True,
                    "label": v
                }
        # Search for {% var <name> <type> %}
        for match in self.rx_vartag.finditer(self.snippet):
            name, type, rest = match.groups()
            vars[name] = {
                "type": type,
                "required": True,
                "label": name
            }
            if rest:
                for a in shlex.split(rest.strip()):
                    k, v = a.split("=", 1)
                    if k == "label":
                        vars[name][k] = v
        return vars

    def expand(self, data):
        """
        Expand snippet with variables
        """
        return Template(self.snippet).render(Context(data))

    @property
    def effective_permission_name(self):
        if self.permission_name:
            return "sa:runsnippet:" + self.permission_name
        else:
            return "sa:runsnippet:default"

    def save(self, *args, **kwargs):
        super(CommandSnippet, self).save(*args, **kwargs)
        # Create permission if required
        if self.permission_name:
            try:
                Permission.objects.get(name=self.effective_permission_name)
            except Permission.DoesNotExist:
                Permission(name=self.effective_permission_name).save()
