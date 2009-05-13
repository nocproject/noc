# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django's standard views module
## for IP space management module
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.shortcuts import get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseForbidden
from django import forms

from noc.ip.models import VRFGroup,VRF,IPv4BlockAccess,IPv4Block,IPv4Address
from noc.peer.models import AS
from noc.lib.render import render,render_success,render_failure
from noc.lib.validators import is_rd,is_cidr,is_int,is_ipv4,is_fqdn
from noc.lib.ip import normalize_prefix,contains
from noc.settings import config
import csv,cStringIO,datetime,subprocess,re

##
## VRF list
##
def index(request):
    l=[]
    for vg in VRFGroup.objects.all():
        vrfs=vg.vrf_set.all()
        if len(vrfs)>0:
            l.append((vg,vrfs.order_by("name")))
    return render(request,"ip/index.html",{"groups":l})
##
## Allocated blocks in VRF
##
def vrf_index(request,vrf_id,prefix="0.0.0.0/0"):
    vrf_id=int(vrf_id)
    vrf=get_object_or_404(VRF,id=vrf_id)
    parents=vrf.prefix(prefix).parents
    prefixes=vrf.prefixes(prefix)
    can_allocate=IPv4BlockAccess.check_write_access(request.user,vrf,prefix)
    prefix=vrf.prefix(prefix)
    return render(request,"ip/vrf_index.html",{"vrf":vrf,"parents":parents,"prefixes":prefixes,"prefix":prefix,
                        "can_allocate":can_allocate})
##
## Allocate new block handler
##
class AllocateBlockForm(forms.Form):
    prefix=forms.CharField(label="prefix",required=True)
    description=forms.CharField(label="description",required=True)
    asn=forms.ModelChoiceField(label="ASN",queryset=AS.objects.all(),required=True)
    tt=forms.IntegerField(label="TT #",required=False)
    def clean_prefix(self):
        if not is_cidr(self.cleaned_data["prefix"]):
            raise forms.ValidationError("Invalid prefix")
        return normalize_prefix(self.cleaned_data["prefix"])

def allocate_block(request,vrf_id,prefix=None):
    vrf=get_object_or_404(VRF,id=int(vrf_id))
    if prefix:
        assert is_cidr(prefix)
        block=get_object_or_404(IPv4Block,vrf=vrf,prefix=prefix)
        initial={
            "prefix"      : block.prefix,
            "description" : block.description,
            "asn"         : block.asn.id,
            "tt"          : block.tt
        }
        p="/"+prefix
    else:
        initial={}
        p=""
    if request.POST:
        form=AllocateBlockForm(request.POST)
        if form.is_valid():
            if not IPv4BlockAccess.check_write_access(request.user,vrf,form.cleaned_data["prefix"]):
                return HttpResponseForbidden("Permission denied")
            if prefix:
                block.prefix=form.cleaned_data["prefix"]
                block.description=form.cleaned_data["description"]
                block.asn=form.cleaned_data["asn"]
                block.tt=form.cleaned_data["tt"]
            else:
                block=IPv4Block(vrf=vrf,prefix=form.cleaned_data["prefix"],
                    description=form.cleaned_data["description"],
                    asn=form.cleaned_data["asn"],
                    modified_by=request.user,
                    tt=form.cleaned_data["tt"])
            block.save()
            return HttpResponseRedirect("/ip/%d/%s/"%(vrf.id,block.prefix))
    else:
        form=AllocateBlockForm(initial=initial)
    return render(request,"ip/allocate_block.html",{"vrf":vrf,"form":form,"p":p})
##
## Deallocate block handler
##
def deallocate_block(request,vrf_id,prefix):
    assert is_cidr(prefix)
    vrf_id=int(vrf_id)
    vrf=get_object_or_404(VRF,id=vrf_id)
    block=get_object_or_404(IPv4Block,vrf=vrf,prefix=prefix)
    if not IPv4BlockAccess.check_write_access(request.user,vrf,prefix):
        return HttpResponseForbidden("Permission denied")
    parents=vrf.prefix(prefix).parents
    parent=parents[-1].prefix
    block.delete()
    return HttpResponseRedirect("/ip/%d/%s/"%(vrf_id,parent))
##
## Assign new IP address handler
##
class AssignAddressForm(forms.Form):
    fqdn=forms.CharField(label="FQDN",required=True)
    ip=forms.CharField(label="IP",required=True)
    description=forms.CharField(label="Description",required=False)
    tt=forms.IntegerField(label="TT #",required=False)
    def clean_fqdn(self):
        if not is_fqdn(self.cleaned_data["fqdn"]):
            raise forms.ValidationError("Invalid FQDN")
        return self.cleaned_data["fqdn"].strip()
    def clean_ip(self):
        if not is_ipv4(self.cleaned_data["ip"]):
            raise forms.ValidationError("Invalid IP Address")
        return self.cleaned_data["ip"]

rx_url_cidr=re.compile(r"^.*/(\d+\.\d+\.\d+\.\d+/\d+)/$")

def assign_address(request,vrf_id,ip=None):
    vrf=get_object_or_404(VRF,id=int(vrf_id))
    if ip:
        assert is_ipv4(ip)
        address=get_object_or_404(IPv4Address,vrf=vrf,ip=ip)
        initial={
            "fqdn"        : address.fqdn,
            "ip"          : address.ip,
            "description" : address.description,
            "tt"          : address.tt,
        }
        p="/"+ip
    else:
        initial={}
        p=""
    if request.POST:
        form=AssignAddressForm(request.POST)
        if form.is_valid():
            assert is_ipv4(form.cleaned_data["ip"])
            assert is_fqdn(form.cleaned_data["fqdn"])
            if not IPv4BlockAccess.check_write_access(request.user,vrf,form.cleaned_data["ip"]+"/32"):
                return HttpResponseForbidden("Permission denied")
            if ip:
                address.fqdn=form.cleaned_data["fqdn"]
                address.ip=form.cleaned_data["ip"]
                address.description=form.cleaned_data["description"]
                address.tt=form.cleaned_data["tt"]
            else:
                # Check no duplicated IPs
                if IPv4Address.objects.filter(vrf=vrf,ip=form.cleaned_data["ip"]).count()>0:
                    return render_failure(request,"Duplicated IP address","Address %s is already present in VRF %s"%(form.cleaned_data["ip"],vrf.name))
                address=IPv4Address(vrf=vrf,fqdn=form.cleaned_data["fqdn"],
                    ip=form.cleaned_data["ip"],description=form.cleaned_data["description"],
                    modified_by=request.user)
            address.save()
            return HttpResponseRedirect("/ip/%d/%s/"%(vrf.id,address.parent.prefix))
    else:
        if "ip" not in initial:
            # Try to calculate ip address from referer
            referer=request.META.get("HTTP_REFERER",None)
            if referer:
                match=rx_url_cidr.match(referer)
                if match and is_cidr(match.group(1)):
                    block=match.group(1)
                    # Find first free IP address
                    from django.db import connection
                    c=connection.cursor()
                    c.execute("SELECT free_ip(%s,%s)",[vrf.id,block])
                    ip=c.fetchall()[0][0]
                    if ip:
                        initial["ip"]=ip
                    else:
                        initial["ip"]="NO FREE IP"
        form=AssignAddressForm(initial=initial)
    return render(request,"ip/assign_address.html",{"vrf":vrf,"form":form,"p":p})
##
## Deallocate ip address handler
##
def revoke_address(request,vrf_id,ip):
    assert is_ipv4(ip)
    vrf_id=int(vrf_id)
    vrf=get_object_or_404(VRF,id=vrf_id)
    address=get_object_or_404(IPv4Address,vrf=vrf,ip=ip)
    if not IPv4BlockAccess.check_write_access(request.user,vrf,ip+"/32"):
        return HttpResponseForbidden("Permission denied")
    prefix=address.parent.prefix
    address.delete()
    return HttpResponseRedirect("/ip/%d/%s/"%(vrf_id,prefix))
##
## An index of tools available for block
##
def block_tools(request,vrf_id,prefix):
    assert is_cidr(prefix)
    vrf_id=int(vrf_id)
    vrf=get_object_or_404(VRF,id=vrf_id)
    if not IPv4BlockAccess.check_write_access(request.user,vrf,prefix):
        return HttpResponseForbidden("Permission denied")
    return render(request,"ip/tools.html",{"vrf":vrf,"prefix":prefix,"upload_ips_form":IPUploadForm(),"upload_ips_axfr_form":AXFRForm()})
##
## Download block's allocated IPs in CSV format
## Columns are: ip,fqdn,description,tt
##
def download_ips(request,vrf_id,prefix):
    def to_utf8(x):
        if x:
            return x.encode("utf8")
        else:
            return ""
    assert is_cidr(prefix)
    vrf_id=int(vrf_id)
    vrf=get_object_or_404(VRF,id=vrf_id)
    if not IPv4BlockAccess.check_write_access(request.user,vrf,prefix):
        return HttpResponseForbidden("Permission denied")
    block=get_object_or_404(IPv4Block,vrf=vrf,prefix=prefix)
    out=cStringIO.StringIO()
    writer=csv.writer(out)
    for a in block.addresses:
        writer.writerow([a.ip,a.fqdn,to_utf8(a.description),a.tt])
    return HttpResponse(out.getvalue(),mimetype="text/csv")
##
## Upload allocated IPs in CSV format
## CSV should contain two to four columns rows (ip,fqdn, description, tt)
##
class IPUploadForm(forms.Form):
    file=forms.FileField()
    
def upload_ips(request,vrf_id,prefix):
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
        return HttpResponseForbidden("Permission denied")
    if request.method=="POST":
        form = IPUploadForm(request.POST, request.FILES)
        if form.is_valid():
            count=upload_csv(request.FILES['file'])
            return render_success(request,"CSV file uploaded","%d IP addresses updated"%count)
    return HttpResponseRedirect("/ip/%d/%s/tools/"%(vrf_id,prefix))
##
## Import IP addresses from zone transfer
##
class AXFRForm(forms.Form):
    ns=forms.CharField()
    zone=forms.CharField()
    source_address=forms.IPAddressField(required=False)

def upload_axfr(request,vrf_id,prefix):
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
        return HttpResponseForbidden("Permission denied")
    if request.POST:
        form=AXFRForm(request.POST)
        if form.is_valid():
            opts=[]
            if form.cleaned_data["source_address"]:
                opts+=["-b",form.cleaned_data["source_address"]]
            pipe = subprocess.Popen([config.get("path","dig")]+opts+["axfr","@%s"%form.cleaned_data["ns"],form.cleaned_data["zone"]],
                shell=False, stdout=subprocess.PIPE).stdout
            data=pipe.read()
            pipe.close()
            count=upload_axfr(data.split("\n"))
            return render_success(request,"Zone transfered","%d IP addresses updated"%count)
    return HttpResponseRedirect("/ip/%d/%s/tools/"%(vrf_id,prefix))
