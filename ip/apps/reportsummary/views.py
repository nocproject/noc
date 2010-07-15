# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Summary Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport,TableColumn
from noc.ip.models import VRF
from noc.lib.validators import is_cidr
from lib.ip import free_blocks,bits_to_size,prefix_to_size
from django import forms
import math
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
class ReportSummary(SimpleReport):
    title="Block Summary"
    form=ReportForm
    def get_data(self,vrf,prefix,**kwargs):
        allocated=self.execute("""
            SELECT prefix
            FROM ip_ipv4block b
            WHERE vrf_id=%s
                AND prefix<<%s::cidr
                AND (SELECT COUNT(*) FROM ip_ipv4block bb WHERE vrf_id=%s AND bb.prefix<<b.prefix)=0
            ORDER BY prefix
            """,[vrf.id,prefix,vrf.id])
        allocated=[a[0] for a in allocated]
        allocated_30=self.execute("""
            SELECT prefix
            FROM ip_ipv4block b
            WHERE vrf_id=%s
                AND prefix<<%s::cidr
                AND masklen(prefix)=30
                AND (SELECT COUNT(*) FROM ip_ipv4block bb WHERE vrf_id=%s AND bb.prefix<<b.prefix)=0
            ORDER BY prefix
            """,[vrf.id,prefix,vrf.id])
        allocated_30=[a[0] for a in allocated_30]
        free=free_blocks(prefix,allocated)
        m,n=prefix.split("/")
        total_addresses=bits_to_size(int(n))
        allocated_addresses=sum([prefix_to_size(x) for x in allocated])
        allocated_30_addresses=sum([prefix_to_size(x) for x in allocated_30])
        free_addresses=sum([prefix_to_size(x) for x in free])
        a_s=len(allocated)
        if a_s:
            avg_allocated_size=float(allocated_addresses)/float(a_s)
        else:
            avg_allocated_size=0.0
        data=[
            ["Total addresses",     total_addresses],
            ["Allocated",           allocated_addresses],
            ["....in /30 networks", allocated_30_addresses],
            ["Free",                free_addresses],
            ["Avegage allocated block size", "%8.2f"%avg_allocated_size],
            ["Average allocated network (bits)",32-int(math.ceil(math.log(avg_allocated_size,2)))]
        ]
        return self.from_dataset(title=self.title+" for "+prefix,
            columns=["",TableColumn("",format="numeric",align="right")],
            data=data)
