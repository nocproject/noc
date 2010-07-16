# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Expanded Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport
from noc.ip.models import VRF,IPv4Block
from noc.lib.validators import is_cidr
from django import forms
from django.shortcuts import get_object_or_404
##
##
##
class ReportForm(forms.Form):
    vrf=forms.ModelChoiceField(label="VRF",queryset=VRF.objects)
    prefix=forms.CharField(label="Prefix",initial="0.0.0.0/0")
    
    def clean_prefix(self):
        prefix=self.cleaned_data.get("prefix","").strip()
        if not is_cidr(prefix):
            raise forms.ValidationError("Invalid prefix")
        return prefix
##
##
##
class ExpandedReport(SimpleReport):
    form=ReportForm
    title="All Allocated Blocks"
    def get_data(self,vrf,prefix,**kwargs):
        def get_info(prefix,level=0):
            s="----"*level
            data=[[s+prefix.prefix,unicode(prefix.vc) if prefix.vc else "",prefix.description]]
            for c in prefix.children:
                data+=get_info(c,level+1)
            return data
        root=get_object_or_404(IPv4Block,vrf=vrf,prefix=prefix)
        data=get_info(root)
        return self.from_dataset(title=self.title+" inside "+prefix,
            columns=["Prefix","VC","Description"],
            data=data,enumerate=True)
