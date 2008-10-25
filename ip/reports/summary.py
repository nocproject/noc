from noc.main.report import Column
import noc.main.report
from noc.ip.models import VRF
from lib.validators import is_cidr
from lib.ip import free_blocks,bits_to_size,prefix_to_size
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
    name="ip.summary"
    title="IP Block summary"
    form_class=ReportForm
    requires_cursor=True
    columns=[Column("Name"),Column("Value",align="LEFT")]
    
    def get_queryset(self):
        vrf_id=self.form.cleaned_data["vrf"].id
        prefix=self.form.cleaned_data["prefix"]
        allocated=self.execute("""
            SELECT prefix
            FROM ip_ipv4block b
            WHERE vrf_id=%s
                AND prefix_cidr<<%s::cidr
                AND (SELECT COUNT(*) FROM ip_ipv4block bb WHERE vrf_id=%s AND bb.prefix_cidr<<b.prefix_cidr)=0
            ORDER BY prefix_cidr
        """,[vrf_id,prefix,vrf_id])
        allocated=[a[0] for a in allocated]
        allocated_30=self.execute("""
            SELECT prefix
            FROM ip_ipv4block b
            WHERE vrf_id=%s
                AND prefix_cidr<<%s::cidr
                AND masklen(prefix_cidr)=30
                AND (SELECT COUNT(*) FROM ip_ipv4block bb WHERE vrf_id=%s AND bb.prefix_cidr<<b.prefix_cidr)=0
            ORDER BY prefix_cidr
        """,[vrf_id,prefix,vrf_id])
        allocated_30=[a[0] for a in allocated_30]
        free=free_blocks(prefix,allocated)
        m,n=prefix.split("/")
        total_addresses=bits_to_size(int(n))
        allocated_addresses=sum([prefix_to_size(x) for x in allocated])
        allocated_30_addresses=sum([prefix_to_size(x) for x in allocated_30])
        free_addresses=sum([prefix_to_size(x) for x in free])
        return [
            ["Total addresses",     total_addresses],
            ["Allocated",           allocated_addresses],
            ["....in /30 networks", allocated_30_addresses],
            ["Free",                free_addresses],
        ]