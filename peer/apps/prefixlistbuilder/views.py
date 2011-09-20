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
from noc.lib.app import Application, view
from noc.peer.models import PeeringPoint, WhoisCache


class PrefixListBuilderForm(forms.Form):
    """
    Builder form
    """
    peering_point = forms.ModelChoiceField(queryset=PeeringPoint.objects.all())
    name = forms.CharField()
    as_set = forms.CharField()

    def clean_as_set(self):
        as_set = self.cleaned_data["as_set"]
        if not as_set.startswith("AS"):
            raise forms.ValidationError("Invalid AS or as-set")
        return as_set


class PrefixListBuilderAppplication(Application):
    """
    Interactive prefix list builder
    """
    title = "Prefix List Builder"

    @view(url=r"^$", menu="Prefix List Builder", access="view")
    def view_builder(self, request):
        pl = ""
        if request.POST:
            form = PrefixListBuilderForm(request.POST)
            if form.is_valid():
                as_set = form.cleaned_data["as_set"]
                prefixes = sorted(WhoisCache.resolve_as_set_prefixes_maxlen(as_set))
                pp = form.cleaned_data["peering_point"].profile
                pl = pp.generate_prefix_list(form.cleaned_data["name"],
                                             prefixes)
        else:
            form = PrefixListBuilderForm()
        return self.render(request, "builder.html", form=form, prefix_list=pl)
