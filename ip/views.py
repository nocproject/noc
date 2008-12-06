from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseForbidden
from django import forms

from noc.ip.models import VRFGroup,VRF,IPv4BlockAccess,IPv4Block,IPv4Address
from noc.peer.models import AS
from noc.lib.render import render
from noc.lib.validators import is_rd,is_cidr,is_int,is_ipv4,is_fqdn
from noc.lib.ip import normalize_prefix

def index(request):
    search_by_name=None
    search_by_rd=None
    query=None
    if request.POST:
        if request.POST["search"]:
            query=request.POST["search"]
            if is_rd(query):
                search_by_rd=query
            else:
                search_by_name=query
    l=[]
    for vg in VRFGroup.objects.all():
        if search_by_name:
            vrfs=vg.vrf_set.filter(name__icontains=search_by_name)
        elif search_by_rd:
            vrfs=vg.vrf_set.filter(rd__exact=search_by_rd)
        else:
            vrfs=vg.vrf_set.all()
        if len(vrfs)>0:
            l.append((vg,vrfs.order_by("name")))
    if query is None:
        query=""
    return render(request,"ip/index.html",{"groups":l,"query":query})
    
def vrf_index(request,vrf_id,prefix="0.0.0.0/0"):
    vrf_id=int(vrf_id)
    vrf=get_object_or_404(VRF,id=vrf_id)
    parents=vrf.prefix(prefix).parents
    prefixes=vrf.prefixes(prefix)
    can_allocate=IPv4BlockAccess.check_write_access(request.user,vrf,prefix)
    prefix=vrf.prefix(prefix)
    return render(request,"ip/vrf_index.html",{"vrf":vrf,"parents":parents,"prefixes":prefixes,"prefix":prefix,
                        "can_allocate":can_allocate})

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
                address=IPv4Address(vrf=vrf,fqdn=form.cleaned_data["fqdn"],
                    ip=form.cleaned_data["ip"],description=form.cleaned_data["description"],
                    modified_by=request.user)
            address.save()
            return HttpResponseRedirect("/ip/%d/%s/"%(vrf.id,address.parent.prefix))
    else:
        form=AssignAddressForm(initial=initial)
    return render(request,"ip/assign_address.html",{"vrf":vrf,"form":form,"p":p})
    
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
