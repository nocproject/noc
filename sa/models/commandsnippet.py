# ----------------------------------------------------------------------
# CommandSnippet model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import shlex

# Third-party modules
from noc.core.translation import ugettext as _
from noc.core.model.fields import DocumentReferenceField
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.template import Template, Context

# NOC modules
from noc.core.model.base import NOCModel
from noc.aaa.models.permission import Permission
from noc.main.models.label import Label
from noc.inv.models.resourcegroup import ResourceGroup


@Label.model
class CommandSnippet(NOCModel):
    """
    Command snippet
    """

    class Meta(object):
        verbose_name = _("Command Snippet")
        verbose_name_plural = _("Command Snippets")
        db_table = "sa_commandsnippet"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=128, unique=True)
    description = models.TextField(_("Description"))
    snippet = models.TextField(_("Snippet"), help_text=_("Code snippet template"))
    change_configuration = models.BooleanField(_("Change configuration"), default=False)
    resource_group = DocumentReferenceField(ResourceGroup)
    is_enabled = models.BooleanField(_("Is Enabled?"), default=True)
    timeout = models.IntegerField(_("Timeout (sec)"), default=60)
    require_confirmation = models.BooleanField(_("Require Confirmation"), default=False)
    ignore_cli_errors = models.BooleanField(_("Ignore CLI errors"), default=False)
    # Restrict access to snippet if set
    # effective permission name will be sa:runsnippet:<permission_name>
    permission_name = models.CharField(_("Permission Name"), max_length=64, null=True, blank=True)
    display_in_menu = models.BooleanField(_("Show in menu"), default=False)
    labels = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(
        models.CharField(max_length=250), blank=True, null=True, default=list
    )

    def __str__(self):
        return self.name

    rx_var = re.compile(r"{{\s*([^|}]+?)\s*(?:\|.+?)?}}", re.MULTILINE)
    rx_vartag = re.compile(
        r"\{%\s*var\s+(?P<name>\S+)\s+(?P<type>\S+)(?P<rest>.*)\s*%\}", re.MULTILINE
    )

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
                vars[v] = {"type": "str", "required": True, "label": v}
        # Search for {% var <name> <type> %}
        for match in self.rx_vartag.finditer(self.snippet):
            name, type, rest = match.groups()
            vars[name] = {"type": type, "required": True, "label": name}
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
        super().save(*args, **kwargs)
        # Create permission if required
        if self.permission_name:
            try:
                Permission.objects.get(name=self.effective_permission_name)
            except Permission.DoesNotExist:
                Permission(name=self.effective_permission_name).save()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_commandsnippet")
