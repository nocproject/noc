# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## <<DESCRIPTION>>
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django import forms
from noc.lib.app import Application,HasPerm
from noc.peer.resolver import resolve_as_set_prefixes
from noc.peer.models import PeeringPoint

##
## Prefix list builder form
##
class PrefixListBuilderForm(forms.Form):
    peering_point= forms.ModelChoiceField(queryset=PeeringPoint.objects.all())
    name=forms.CharField()
    as_set=forms.CharField()
    
    def clean_as_set(self):
        as_set=self.cleaned_data["as_set"]
        if not as_set.startswith("AS"):
            raise forms.ValidationError("Invalid AS or as-set")
        return as_set
##
## Prefix List Builder Application
##
class PrefixListBuilderAppplication(Application):
    title="Prefix List Builder"
    ##
    ## Resolve prefix list
    ##
    def view_builder(self,request):
        pl=""
        if request.POST:
            form=PrefixListBuilderForm(request.POST)
            if form.is_valid():
                prefixes=resolve_as_set_prefixes(form.cleaned_data["as_set"],True)
                prefixes=sorted(prefixes)
                pl=form.cleaned_data["peering_point"].profile.generate_prefix_list(form.cleaned_data["name"],prefixes,False)
        else:
            form=PrefixListBuilderForm()
        return self.render(request,"builder.html",{"form":form,"prefix_list":pl})
    view_builder.url=r"^$"
    view_builder.menu="Prefix List Builder"
    view_builder.access=HasPerm("view")
