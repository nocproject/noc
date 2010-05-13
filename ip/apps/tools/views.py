# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Tools
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django import forms
from django.shortcuts import get_object_or_404
from noc.lib.app import Application
from noc.lib.ip import contains
from noc.ip.models import *
from noc.lib.validators import is_cidr,is_ipv4,is_fqdn
import csv,cStringIO,datetime,subprocess
##
## IP Block tooks
##
class ToolsAppplication(Application):
    ##
    ## An index of tools available for block
    ##
    def view_index(self,request,vrf_id,prefix):
        assert is_cidr(prefix),"IPv4 Prefix Required"
        vrf_id=int(vrf_id)
        vrf=get_object_or_404(VRF,id=vrf_id)
        if not IPv4BlockAccess.check_write_access(request.user,vrf,prefix):
            return self.response_forbidden("Permission denied")
        return self.render(request,"index.html",{"vrf":vrf,"prefix":prefix,
            "upload_ips_form":self.IPUploadForm(),
            "upload_ips_axfr_form":self.AXFRForm()})
    view_index.url=r"^(?P<vrf_id>\d+)/(?P<prefix>\d+\.\d+\.\d+\.\d+/\d+)/$"
    view_index.url_name="index"
    view_index.access=Application.has_perm("ip.change_ipv4block")
    ##
    ## Download block's allocated IPs in CSV format
    ## Columns are: ip,fqdn,description,tt
    ##
    def view_download_ip(self,request,vrf_id,prefix):
        def to_utf8(x):
            if x:
                return x.encode("utf8")
            else:
                return ""
        assert is_cidr(prefix),"IPv4 Prefix Required"
        vrf=get_object_or_404(VRF,id=int(vrf_id))
        if not IPv4BlockAccess.check_write_access(request.user,vrf,prefix):
            return self.response_forbidden("Permission denied")
        block=get_object_or_404(IPv4Block,vrf=vrf,prefix=prefix)
        out=cStringIO.StringIO()
        writer=csv.writer(out)
        for a in block.nested_addresses:
            writer.writerow([a.ip,a.fqdn,to_utf8(a.description),a.tt])
        return self.render_response(out.getvalue(),content_type="text/csv")
    view_download_ip.url=r"^(?P<vrf_id>\d+)/(?P<prefix>\d+\.\d+\.\d+\.\d+/\d+)/download_ip/$"
    view_download_ip.url_name="download_ip"
    view_download_ip.access=Application.has_perm("ip.change_ipv4block")
    ##
    ## IP Upload form
    ##
    class IPUploadForm(forms.Form):
        file=forms.FileField()
    ##
    ## Upload allocated IPs in CSV format
    ## CSV should contain two to four columns rows (ip,fqdn, description, tt)
    ##
    def view_upload_ip(self,request,vrf_id,prefix):
        def upload_csv(file):
            count=0
            reader=csv.reader(file)
            for row in reader:
                if len(row)<2:
                    continue
                if not is_ipv4(row[0]) or not is_fqdn(row[1]):
                    continue
                # Leave only addresses residing into "prefix"
                # To prevent uploading to not-owned blocks
                if not contains(prefix,row[0]):
                    continue
                changed=False
                try:
                    a=IPv4Address.objects.get(vrf=vrf,ip=row[0])
                except IPv4Address.DoesNotExist:
                    a=IPv4Address(vrf=vrf,ip=row[0])
                    changed=True
                if a.fqdn!=row[1]:
                    a.fqdn=row[1]
                    changed=True
                if len(row)>=3 and row[2]:
                    a.description=row[2]
                    changed=True
                if len(row)>=4 and row[3]:
                    a.tt=row[3]
                    changed=True
                if changed:
                    a.modified_by=request.user
                    a.last_modified=datetime.datetime.now()
                    a.save()
                    count+=1
            return count
        assert is_cidr(prefix)
        vrf_id=int(vrf_id)
        vrf=get_object_or_404(VRF,id=vrf_id)
        if not IPv4BlockAccess.check_write_access(request.user,vrf,prefix):
            return self.response_forbidden("Permission denied")
        if request.method=="POST":
            form = self.IPUploadForm(request.POST, request.FILES)
            if form.is_valid():
                count=upload_csv(request.FILES['file'])
                self.message_user(request,"%d IP addresses uploaded from CSV"%count)
                return self.response_redirect("%s%d/%s/"%(self.base_url,vrf.id,prefix))
        return self.response_redirect("%s%d/%s/"%(self.base_url,vrf.id,prefix))
    view_upload_ip.url=r"^(?P<vrf_id>\d+)/(?P<prefix>\d+\.\d+\.\d+\.\d+/\d+)/upload_ip/$"
    view_upload_ip.url_name="upload_ip"
    view_upload_ip.access=Application.has_perm("ip.change_ipv4block")
    ##
    ## Zone import form
    ##
    class AXFRForm(forms.Form):
        ns=forms.CharField()
        zone=forms.CharField()
        source_address=forms.IPAddressField(required=False)
    ##
    ## Import via zone transfer
    ##
    def view_upload_axfr(self,request,vrf_id,prefix):
        def upload_axfr(data):
            count=0
            for row in data:
                row=row.strip()
                if row=="" or row.startswith(";"):
                    continue
                row=row.split()
                if len(row)!=5 or row[2]!="IN" or row[3]!="PTR":
                    continue
                if row[3]=="PTR":
                    x=row[0].split(".")
                    ip="%s.%s.%s.%s"%(x[3],x[2],x[1],x[0])
                    fqdn=row[4]
                    if fqdn.endswith("."):
                        fqdn=fqdn[:-1]
                # Leave only addresses residing into "prefix"
                # To prevent uploading to not-owned blocks
                if not contains(prefix,ip):
                    continue
                changed=False
                try:
                    a=IPv4Address.objects.get(vrf=vrf,ip=ip)
                except IPv4Address.DoesNotExist:
                    a=IPv4Address(vrf=vrf,ip=ip)
                    changed=True
                if a.fqdn!=fqdn:
                    a.fqdn=fqdn
                    changed=True
                if changed:
                    a.modified_by=request.user
                    a.last_modified=datetime.datetime.now()
                    a.save()
                    count+=1
            return count
        assert is_cidr(prefix)
        vrf_id=int(vrf_id)
        vrf=get_object_or_404(VRF,id=vrf_id)
        if not IPv4BlockAccess.check_write_access(request.user,vrf,prefix):
            return self.response_forbidden("Permission denied")
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
                self.message_user(request,"%d IP addresses uploaded via zone transfer"%count)
                return self.response_redirect("%s%d/%s/"%(self.base_url,vrf.id,prefix))
        return self.response_redirect("%s%d/%s/"%(self.base_url,vrf.id,prefix))
    view_upload_axfr.url=r"^(?P<vrf_id>\d+)/(?P<prefix>\d+\.\d+\.\d+\.\d+/\d+)/upload_axfr/$"
    view_upload_axfr.url_name="upload_axfr"
    view_upload_axfr.access=Application.has_perm("ip.change_ipv4block")