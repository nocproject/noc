# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interactive prefix list builder
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django import forms
from django.core.validators import RegexValidator
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.peer.models import PeeringPoint, WhoisCache

as_set_re = "^AS(?:\d+|-\S+)(:\S+)?(?:\s+AS(?:\d+|-\S+)(:\S+)?)*$"


class PrefixListBuilderForm(forms.Form):
    """
    Builder form
    """
    peering_point = forms.ModelChoiceField(queryset=PeeringPoint.objects.all())
    name = forms.CharField(required=False)
    as_set = forms.CharField(validators=[RegexValidator(as_set_re)])

    def clean(self):
        if not self.cleaned_data["name"] and "as_set" in self.cleaned_data:
            self.cleaned_data["name"] = self.cleaned_data["as_set"]
        return self.cleaned_data


class PrefixListBuilderAppplication(ExtApplication):
    """
    Interactive prefix list builder
    """
    title = "Prefix List Builder"
    menu = "Prefix List Builder"
    #implied_permissions = {
    #    "read": ["peer:peeringpoint:lookup"]
    #}

    @view(method=["GET"], url=r"^$", access="read", api=True,
          validate=PrefixListBuilderForm)
    def api_list(self, request, peering_point, name, as_set):
        prefixes = WhoisCache.resolve_as_set_prefixes_maxlen(as_set)
        pl = peering_point.profile.generate_prefix_list(name, prefixes)
        return {
            "name": name,
            "prefix_list": pl,
            "success" : True
        }
