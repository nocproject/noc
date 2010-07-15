# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Free Blocks Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport
from noc.ip.models import VRF
from noc.lib.validators import is_cidr
from django import forms
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
class FreeBlocksReport(SimpleReport):
    title="Free Blocks"
    form=ReportForm
    def get_data(self,vrf,prefix,**kwargs):
        
        return self.from_query(title=self.title,
            columns=["Free Block"],
            query="""SELECT prefix
                FROM ip_ipv4block b
                WHERE vrf_id=%s
                    AND prefix<<%s::cidr
                    AND (SELECT COUNT(*) FROM ip_ipv4block bb WHERE vrf_id=%s AND bb.prefix<<b.prefix)=0
                ORDER BY prefix""",
            params=[vrf.id,prefix,vrf.id])
