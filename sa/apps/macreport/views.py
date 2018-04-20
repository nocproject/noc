# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MAC Report Application
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.saapplication import SAApplication
from django import forms
from noc.sa.interfaces import VLANIDParameter,MACAddressParameter
from noc.vc.models import VCDomain
##
##
##
def reduce_macreport(task,vc_domain=None):
    def vc_name(vlan_id):
        if vc_domain:
            try:
                vc=VC.objects.get(vc_domain=vc_domain,l1=vlan_id)
                return "%s<br/><i>(%s)</i>"%(vlan_id,vc.name)
            except VC.DoesNotExist:
                return str(vlan_id)
        else:
            return str(vlan_id)
    from noc.vc.models import VC
    data={} # vlan -> mac -> [(object,interface,type)]
    vlan_macs={}
    for mt in task.maptask_set.all():
        if mt.status!="C":
            continue
        # Collect data from task
        for r in mt.script_result:
            vlan_id=r["vlan_id"]
            mac=r["mac"]
            interfaces=r["interfaces"]
            if vlan_id not in data:
                data[vlan_id]={}
            if mac not in data[vlan_id]:
                data[vlan_id][mac]=[]
            data[vlan_id][mac]+=[(mt.managed_object.name,", ".join(interfaces),r["type"])]
    # Render result
    r=["<table border='1'>","<thead>","<tr>","<th>VLAN</th>","<th>MAC</th>","<th>Object</th>","<th>Port</th>","<th>Type</th>","</tr>","</thead>","<tbody>"]
    for vlan_id in sorted(data.keys()):
        v_macs=0
        vlan_name=vc_name(vlan_id)
        vd=sorted(data[vlan_id].items(),lambda x,y:cmp(x[0],y[0]))
        r+=["<tr>","<td rowspan='%d'>%s</td>"%(reduce(lambda x,y:x+len(y[1]),vd,0),vlan_name)]
        # Display first row
        mac,idata=vd.pop(0)
        idata=sorted(idata,lambda x,y:cmp(x[0],y[0]))
        name,interfaces,type=idata.pop(0)
        v_macs+=1
        r+=["<td rowspan='%d'>%s</td>"%(len(idata)+1,mac),"<td>%s</td>"%name,"<td>%s</td>"%interfaces,"<td>%s</td>"%type,"</tr>"]
        while vd or idata:
            while idata:
                name,interfaces,type=idata.pop(0)
                r+=["<tr>","<td>%s</td>"%name,"<td>%s</td>"%interfaces,"<td>%s</td>"%type,"</tr>"]
            if vd:
                mac,idata=vd.pop(0)
                name,interfaces,type=idata.pop(0)
                r+=["<tr>","<td rowspan='%d'>%s</td>"%(len(idata)+1,mac),"<td>%s</td>"%name,"<td>%s</td>"%interfaces,"<td>%s</td>"%type,"</tr>"]
                v_macs+=1
        vlan_macs[vlan_name]=v_macs
    r+=["</tbody>","</table>"]
    r+=["<br/>"]
    # Vlan MAC summary
    mac_count=reduce(lambda x,y:x+y,vlan_macs.values(),0)
    r+=["<br/>"]
    r+=["<b>MAC Summary</b>"]
    r+=["<table border='0'>"]
    for vlan,c in sorted(vlan_macs.items(),lambda x,y:-cmp(x[1],y[1])):
        r+=["<tr>","<td>%s</td>"%vlan,"<td align='right'>%d</td>"%c,"</tr>"]
    r+=["<tr>","<td>Total:</td>","<td align='right'>%s</td>"%mac_count,"</tr>"]
    r+=["</table>"]
    # Summary
    r+=["<br/>"]
    r+=["<b>Summary</b>"]
    r+=["<table border='0'>"]
    r+=["<tr>","<td>Total VLANs</td>","<td align='right'>%d</td>"%len(data),"</tr>"]
    r+=["<tr>","<td>Total MACs</td>","<td align='right'>%d</td>"%mac_count,"</tr>"]
    r+=["</table>"]
    return "\n".join(r)
##
##
##
class MACReportAppplication(SAApplication):
    title="MAC Report"
    menu="Tasks | MAC Report"
    reduce_task=reduce_macreport
    map_task="get_mac_address_table"
    class MACReportForm(forms.Form):
        vlan=forms.IntegerField(required=False)
        mac=forms.CharField(required=False)
        vc_domain=forms.ModelChoiceField(required=False,queryset=VCDomain.objects,help_text="Display VLAN descriptions if selected")
        def clean_vlan(self):
            return VLANIDParameter(required=False).form_clean(self.cleaned_data["vlan"])
        def clean_mac(self):
            return MACAddressParameter(required=False).form_clean(self.cleaned_data["mac"])
    form=MACReportForm
    ##
    ## Prepare map paramters
    ##
    def clean_map(self,data):
        r={}
        for n in ["vlan","mac"]:
            if data[n]:
                r[n]=data[n]
        return r
    ##
    ##
    ##
    def clean_reduce(self,data):
        return {"vc_domain":data["vc_domain"]}
