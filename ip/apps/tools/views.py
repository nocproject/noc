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
            upload_ips_axfr_form=self.AXFRForm(), rebase_form=self.RebaseForm(prefix.prefix))
    
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
        writer.writerow(["address","fqdn","mac","description","tt","tags"])
        for a in prefix.nested_address_set.order_by("address"):
            writer.writerow([a.address,a.fqdn,a.mac,to_utf8(a.description),a.tt,a.tags])
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
                if not p.contains(IPv4(ip)):
                    continue
                a,changed=Address.objects.get_or_create(vrf=vrf,afi=afi,address=ip)
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
    ##
    ## Rebase prefix
    ##
    class RebaseForm(NOCForm):
        vrf=forms.ModelChoiceField(label="VRF", queryset=VRF.objects.filter())
        to_prefix=forms.CharField(label="Rebase to prefix")
        
        def __init__(self, prefix, data=None):
            super(ToolsAppplication.RebaseForm, self).__init__(data)
            self.prefix=prefix
        
        def clean_to_prefix(self):
            to_prefix=self.cleaned_data["to_prefix"]
            check_prefix(to_prefix)
            p0=IP.prefix(self.prefix)
            p1=IP.prefix(to_prefix)
            if p0==p1:
                raise forms.ValidationError("Cannot rebase prefix to self")
            if p0.afi!=p1.afi:
                raise forms.ValidationError("Cannot change address family during rebase")
            if p0.mask<p1.mask:
                raise forms.ValidationError("Cannot rebase to prefix of lesser size")
            return to_prefix
        
    
    @view(url=r"^(?P<vrf_id>\d+)/(?P<afi>[46])/(?P<prefix>\S+)/rebase/$",
        url_name="rebase",
        access=HasPerm("view"))
    def view_rebase(self, request, vrf_id, afi, prefix):
        vrf=self.get_object_or_404(VRF,id=int(vrf_id))
        prefix=self.get_object_or_404(Prefix, vrf=vrf, afi=afi, prefix=prefix)
        if request.POST:
            form=self.RebaseForm(prefix.prefix, request.POST)
            if form.is_valid():
                # Rebase prefix
                new_prefix=prefix.rebase(form.cleaned_data["vrf"], form.cleaned_data["to_prefix"])
                self.message_user(request, _(u"Prefix %(old_prefix)s is rebased to %(new_prefix)s") % {
                    "old_prefix": prefix,
                    "new_prefix": form.cleaned_data["to_prefix"]})
                return self.response_redirect("ip:ipam:vrf_index",new_prefix.vrf.id,afi,new_prefix.prefix)
        else:
            form=self.RebaseForm(prefix.prefix)
        return self.render(request, "index.html", vrf=vrf, afi=afi, prefix=prefix, rebase_form=form)
    

    