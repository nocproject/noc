# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Tools
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python Modules
import csv
import cStringIO
import datetime
import subprocess
# Django Modules
from django.utils.translation import ugettext_lazy as _
from django import forms
# NOC Modules
from noc.lib.app import Application,HasPerm,view
from noc.lib.ip import *
from noc.ip.models import *
from noc.lib.validators import *
from noc.lib.forms import *
from noc.settings import config

##
## IP Block tooks
##
class ToolsAppplication(Application):
    title="Tools"
    ##
    ## An index of tools available for block
    ##
    @view(  url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+?/\d+)/$",
            url_name="index",
            access=HasPerm("view"))
    def view_index(self,request,vrf_id,afi,prefix):
        vrf=self.get_object_or_404(VRF,id=int(vrf_id))
        prefix=self.get_object_or_404(Prefix,vrf=vrf,afi=afi,prefix=prefix)
        if not prefix.can_change(request.user):
            return self.response_forbidden(_("Permission denined"))
        return self.render(request,"index.html",vrf=vrf,afi=afi,prefix=prefix,
            upload_ips_axfr_form=self.AXFRForm())
    
    ##
    ## Download block's allocated IPs in CSV format
    ## Columns are: ip,fqdn,description,tt
    ##
    @view(  url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/download_ip/$",
            url_name="download_ip",
            access=HasPerm("view"))
    def view_download_ip(self,request,vrf_id,afi,prefix):
        def to_utf8(x):
            if x:
                return x.encode("utf8")
            else:
                return ""
        
        vrf=self.get_object_or_404(VRF,id=int(vrf_id))
        prefix=self.get_object_or_404(Prefix,vrf=vrf,afi=afi,prefix=prefix)
        if not prefix.can_change(request.user):
            return self.response_forbidden(_("Permission denined"))
        out=cStringIO.StringIO()
        writer=csv.writer(out)
        writer.writerow(["address","fqdn","description","tt","tags"])
        for a in prefix.address_set.order_by("address"):
            writer.writerow([a.address,a.fqdn,to_utf8(a.description),a.tt,a.tags])
        return self.render_response(out.getvalue(),content_type="text/csv")
    
    ##
    ## Zone import form
    ##
    class AXFRForm(NOCForm):
        ns=forms.CharField(label=_("NS"),help_text=_("Name server IP address. NS must have zone transfer enabled for NOC host"))
        zone=forms.CharField(label=_("Zone"),help_text=_("DNS Zone name to transfer"))
        source_address=forms.IPAddressField(label=_("Source Address"),required=False,
                        help_text=_("Source address to issue zone transfer"))
    
    ##
    ## Import via zone transfer
    ##
    @view(  url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/upload_axfr/$",
        url_name="upload_axfr",
        access=HasPerm("view"))
    def view_upload_axfr(self,request,vrf_id,afi,prefix):
        def upload_axfr(data):
            p=IP.prefix(prefix.prefix)
            count=0
            for row in data:
                row=row.strip()
                if row=="" or row.startswith(";"):
                    continue
                row=row.split()
                if len(row)!=5 or row[2]!="IN" or row[3]!="PTR":
                    continue
                if row[3]=="PTR":
                    # @todo: IPv6
                    x=row[0].split(".")
                    ip="%s.%s.%s.%s"%(x[3],x[2],x[1],x[0])
                    fqdn=row[4]
                    if fqdn.endswith("."):
                        fqdn=fqdn[:-1]
                # Leave only addresses residing into "prefix"
                # To prevent uploading to not-owned blocks
                if p.contains(IPv4(ip)):
                    continue
                a,changed=Address.get_or_create(Address,vrf=vrf,afi=afi,address=ip)
                if a.fqdn!=fqdn:
                    a.fqdn=fqdn
                    changed=True
                if changed:
                    a.save()
                    count+=1
            return count
        
        vrf=self.get_object_or_404(VRF,id=int(vrf_id))
        prefix=self.get_object_or_404(Prefix,vrf=vrf,afi=afi,prefix=prefix)
        if not prefix.can_change(request.user):
            return self.response_forbidden(_("Permission denined"))
        if request.POST:
            form=self.AXFRForm(request.POST)
            if form.is_valid():
                opts=[]
                if form.cleaned_data["source_address"]:
                    opts+=["-b",form.cleaned_data["source_address"]]
                pipe = subprocess.Popen([config.get("path","dig")]+opts+["axfr","@%s"%form.cleaned_data["ns"],form.cleaned_data["zone"]],
                    shell=False, stdout=subprocess.PIPE).stdout
                data=pipe.read()
                pipe.close()
                count=upload_axfr(data.split("\n"))
                self.message_user(request,_("%(count)s IP addresses uploaded via zone transfer")%{"count":count})
                return self.response_redirect("ip:ipam:vrf_index",vrf.id,afi,prefix.prefix)
        else:
            form=self.AXFRForm()
        return self.render(request,"index.html",vrf=vrf,afi=afi,prefix=prefix,
            upload_ips_axfr_form=form)
