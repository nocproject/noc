# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column
import noc.main.report
from noc.ip.models import VRF
from lib.validators import is_cidr
from django import forms

class ReportForm(forms.Form):
    vrf=forms.ModelChoiceField(label="VRF",queryset=VRF.objects)
    prefix=forms.CharField(label="Prefix",initial="0.0.0.0/0")
    
    def clean_prefix(self):
        prefix=self.cleaned_data.get("prefix","").strip()
        if not is_cidr(prefix):
            raise forms.ValidationError("Invalid prefix")
        return prefix

class Report(noc.main.report.Report):
    name="ip.allocations"
    title="Allocated Blocks"
    form_class=ReportForm
    requires_cursor=True
    columns=[Column("Block"),Column("Description")]
    
    def get_queryset(self):
        vrf_id=self.form.cleaned_data["vrf"].id
        prefix=self.form.cleaned_data["prefix"]
        return self.execute("""
            SELECT prefix,description
            FROM ip_ipv4block b
            WHERE vrf_id=%s
                AND prefix<<%s::cidr
                AND (SELECT COUNT(*) FROM ip_ipv4block bb WHERE vrf_id=%s AND bb.prefix<<b.prefix)=0
            ORDER BY prefix
        """,[vrf_id,prefix,vrf_id])
