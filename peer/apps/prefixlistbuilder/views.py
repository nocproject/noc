# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interactive prefix list builder
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django import forms
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.peer.models import PeeringPoint, WhoisCache


class PrefixListBuilderForm(forms.Form):
    """
    Builder form
    """
    peering_point = forms.ModelChoiceField(queryset=PeeringPoint.objects.all())
    name = forms.CharField(required=False)
    as_set = forms.CharField()

    def clean(self):
        if not self.cleaned_data["name"] and "as_set" in self.cleaned_data:
            self.cleaned_data["name"] = self.cleaned_data["as_set"]
        return self.cleaned_data

    def clean_as_set(self):
        as_set = self.cleaned_data["as_set"]
        if not as_set.startswith("AS"):
            raise forms.ValidationError("Invalid AS or as-set")
        return as_set


class PrefixListBuilderAppplication(ExtApplication):
    """
    Interactive prefix list builder
    """
    title = "Prefix List Builder"
    menu = "Prefix List Builder"
    implied_permissions = {
        "read": ["peer:peeringpoint:lookup"]
    }

    @view(method=["GET"], url=r"^$", access="read", api=True,
          validate=PrefixListBuilderForm)
    def api_list(self, request, peering_point, name, as_set):
        prefixes = WhoisCache.resolve_as_set_prefixes_maxlen(as_set)
        pl = peering_point.profile.generate_prefix_list(name, prefixes)
        return {
            "name": name,
            "prefix_list": pl
        }
