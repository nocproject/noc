# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IP Address space management application
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.shortcuts import get_object_or_404
from django import forms
from noc.lib.app import Application,URL
from noc.ip.models import *
from noc.vc.models import VC,VCBindFilter
from noc.lib.colors import get_colors
from noc.lib.validators import is_cidr,is_ipv4,is_fqdn
from noc.lib.ip import normalize_prefix,contains,in_range,free_blocks
##
## IP Address Space Management
##
class IPManageAppplication(Application):
    title="Assigned Addresses"
    ##
    ## Display VRF list
    ##
    def view_index(self,request):
        groups=[]
        for vg in VRFGroup.objects.all():
            vrfs=vg.vrf_set.all()
            if len(vrfs)>0:
                groups+=[(vg,vrfs.order_by("name"))]
        return self.render(request,"index.html",{"groups":groups})
    view_index.url=r"^$"
    view_index.menu="Assigned Addresses"
    view_index.access=Application.has_perm("ip.change_ipv4block")
    ##
    ## Display assigned addresses and blocks
    ##
    def view_vrf_index(self,request,vrf_id,prefix="0.0.0.0/0"):
        if not is_cidr(prefix):
            return self.response_not_found("Prefix '%s' is not found"%prefix)
        vrf_id=int(vrf_id)
        vrf=get_object_or_404(VRF,id=vrf_id)
        parents=vrf.prefix(prefix).parents
        prefixes=vrf.prefixes(prefix)
        can_allocate=IPv4BlockAccess.check_write_access(request.user,vrf,prefix)
        prefix=vrf.prefix(prefix)
        has_children=prefix.has_children
        total=prefix.size
        block_info=[
            ("Net",         prefix.prefix),
            ("Netmask",     prefix.netmask),
            ("Broadcast",   prefix.broadcast),
            ("Wildcard",    prefix.wildcard),
            ("Size",        total),
        ]
        ranges=None
        all_addresses=None
        if has_children:
            orphaned_addresses=prefix.orphaned_addresses
        else:
            orphaned_addresses=None
            used=prefix.address_count
            free=total-used
            block_info+=[
                ("Addresses Used",used),
                ("Addresses Free",free),
            ]
            ranges=list(prefix.ranges)
            colors=get_colors(len(ranges))
            rc=[]
            for r,c in zip(ranges,colors):
                r.color=c
                rc+=[(r.from_ip,r.to_ip,c)]
            all_addresses=[]
            for a in prefix.all_addresses:
                try:
                    ip=a.ip
                except:
                    ip=a
                c=None
                for from_ip,to_ip,cl in rc:
                    if in_range(ip,from_ip,to_ip):
                        c=cl
                        break
                all_addresses+=[(c,a)]
        return self.render(request,"vrf_index.html",{"vrf":vrf,"parents":parents,"prefixes":prefixes,"prefix":prefix,
                            "can_allocate":can_allocate,"block_info":block_info,"has_children":has_children,
                            "ranges":ranges,"all_addresses":all_addresses,"orphaned_addresses":orphaned_addresses})
    view_vrf_index.url=r"(?P<vrf_id>\d+)/(?P<prefix>\S+)/$"
    view_vrf_index.url_name="vrf_index"
    view_vrf_index.access=Application.has_perm("ip.change_ipv4block")
    ##
    ## Allocate new block form
    ##
    class AllocateBlockForm(forms.Form):
        prefix=forms.CharField(label="prefix",required=True)
        description=forms.CharField(label="description",required=True)
        asn=forms.ModelChoiceField(label="ASN",queryset=AS.objects.all(),required=True)
        tt=forms.IntegerField(label="TT #",required=False)
        def __init__(self,data=None,initial=None,vrf=None,block_id=None):
            forms.Form.__init__(self,data=data,initial=initial)
            self.vrf=vrf
            self.block_id=block_id
        def clean_prefix(self):
            if not is_cidr(self.cleaned_data["prefix"]):
                raise forms.ValidationError("Invalid prefix")
            prefix=normalize_prefix(self.cleaned_data["prefix"])
            # Check for duplication
            q=IPv4Block.objects.filter(prefix=prefix)
            if self.vrf.vrf_group.unique_addresses:
                q=q.filter(vrf__in=self.vrf.vrf_group.vrf_set.all())
            else:
                q=q.filter(vrf=self.vrf)
            if self.block_id:
                q=q.exclude(id=self.block_id)
            if q.count()>0:
                raise forms.ValidationError("Block is already present")
            return prefix
    ##
    ## Allocate Block
    ##
    def view_allocate_block(self,request,vrf_id,prefix=None):
        rx_referer_prefix=re.compile(r"^.+/(?P<prefix>\d+\.\d+\.\d+\.\d+/\d+)/$")
        vrf=get_object_or_404(VRF,id=int(vrf_id))
        suggestions=[]
        parent=prefix
        block_id=None
        initial={}
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
            block_id=block.id
        else:
            # Fetch prefix from referrer
            match=rx_referer_prefix.match(request.META.get("HTTP_REFERER",""))
            if match and is_cidr(match.group(1)):
                # Suggest blocks of different sizes
                parent=match.group(1)
                free=[(x.split("/")[0],int(x.split("/")[1])) for x in free_blocks(parent,[p.prefix for p in vrf.prefixes(top=parent)])]
                free=sorted(free,lambda x,y: -cmp(x[1],y[1]))
                for m in range(int(parent.split("/")[1])+1,31):
                    for fp,fm in free:
                        if fm<=m:
                            suggestions+=["%s/%d"%(fp,m)]
                            break
                # Fill initial prefix
                prefix=parent.split("/")[0]
                while prefix.endswith(".0"):
                    prefix=prefix[:-2]
                initial["prefix"]=prefix
            p=""
        if request.POST:
            # Process post request
            form=self.AllocateBlockForm(request.POST,vrf=vrf,block_id=block_id)
            if form.is_valid():
                if not IPv4BlockAccess.check_write_access(request.user,vrf,form.cleaned_data["prefix"]):
                    return self.respone_forbidden("Permission denied")
                if prefix:
                    block.prefix=form.cleaned_data["prefix"]
                    block.description=form.cleaned_data["description"]
                    block.asn=form.cleaned_data["asn"]
                    block.tt=form.cleaned_data["tt"]
                    status="changed"
                else:
                    block=IPv4Block(vrf=vrf,prefix=form.cleaned_data["prefix"],
                        description=form.cleaned_data["description"],
                        asn=form.cleaned_data["asn"],
                        modified_by=request.user,
                        tt=form.cleaned_data["tt"])
                    status="created"
                block.save()
                self.message_user(request,"Block '%s' in VRF '%s' %s successfully"%(block.prefix,str(vrf),status))
                return self.response_redirect("%s%d/%s/"%(self.base_url,vrf.id,block.prefix))
        else:
            # Display form
            form=self.AllocateBlockForm(initial=initial)
        return self.render(request,"allocate_block.html",{"vrf":vrf,"form":form,"p":p,"suggestions":suggestions,"parent":parent})
    view_allocate_block.url=[
        URL(r"^(?P<vrf_id>\d+)/allocate_block/",name="allocate_block"),
        URL(r"^(?P<vrf_id>\d+)/(?P<prefix>\S+)/allocate_block/$",name="change_block")
        ]
    view_allocate_block.access=Application.has_perm("ip.change_ipv4block")
    ##
    ## Deallocate block handler
    ##
    def view_deallocate_block(self,request,vrf_id,prefix):
        assert is_cidr(prefix)
        vrf_id=int(vrf_id)
        vrf=get_object_or_404(VRF,id=vrf_id)
        block=get_object_or_404(IPv4Block,vrf=vrf,prefix=prefix)
        if not IPv4BlockAccess.check_write_access(request.user,vrf,prefix):
            return self.response_forbidden("Permission denied")
        parents=vrf.prefix(prefix).parents
        parent=parents[-1].prefix
        block.delete()
        self.message_user(request,"Block %s in VRF %s deallocated successfully"%(prefix,str(vrf)))
        return self.response_redirect("%s%d/%s/"%(self.base_url,vrf_id,parent))
    view_deallocate_block.url=r"^(?P<vrf_id>\d+)/(?P<prefix>\S+)/deallocate_block/$"
    view_deallocate_block.url_name="deallocate_block"
    view_deallocate_block.access=Application.has_perm("ip.change_ipv4block")
    ##
    ##
    ## Assign new IP address form
    ##
    class AssignAddressForm(forms.Form):
        fqdn=forms.CharField(label="FQDN",required=True)
        ip=forms.CharField(label="IP",required=True)
        description=forms.CharField(label="Description",required=False)
        tt=forms.IntegerField(label="TT #",required=False)
        def __init__(self,data=None,initial=None,vrf=None,address_id=None):
            forms.Form.__init__(self,data=data,initial=initial)
            self.vrf=vrf
            self.address_id=address_id
        def clean_fqdn(self):
            if not is_fqdn(self.cleaned_data["fqdn"]):
                raise forms.ValidationError("Invalid FQDN")
            return self.cleaned_data["fqdn"].strip()
        def clean_ip(self):
            if not is_ipv4(self.cleaned_data["ip"]):
                raise forms.ValidationError("Invalid IP Address")
            if IPv4AddressRange.is_range_locked(self.vrf,self.cleaned_data["ip"]):
                raise forms.ValidationError("IP Address Range is locked")
            # Check for duplications
            ip=self.cleaned_data["ip"]
            q=IPv4Address.objects.filter(ip=ip)
            if self.vrf.vrf_group.unique_addresses:
                q=q.filter(vrf__in=self.vrf.vrf_group.vrf_set.all())
            else:
                q=q.filter(vrf=self.vrf)
            if self.address_id:
                q=q.exclude(id=self.address_id)
            if q.count()>0:
                raise forms.ValidationError("IPv4 Address is already present")
            return ip
    ##
    ## Assign IP address
    ##
    def view_assign_address(self,request,vrf_id,ip=None,new_ip=None):
        rx_url_cidr=re.compile(r"^.*/(\d+\.\d+\.\d+\.\d+/\d+)/$")
        vrf=get_object_or_404(VRF,id=int(vrf_id))
        parents=[]
        address_id=None
        if ip:
            assert is_ipv4(ip)
            address=get_object_or_404(IPv4Address,vrf=vrf,ip=ip)
            address_id=address.id
            initial={
                "fqdn"        : address.fqdn,
                "ip"          : address.ip,
                "description" : address.description,
                "tt"          : address.tt,
            }
            p="/"+ip
            parents=list(address.parent.parents)+[address.parent]
        elif new_ip:
            assert is_ipv4(new_ip)
            initial={"ip":new_ip}
            p=""
        else:
            initial={}
            p=""
        if request.POST:
            form=self.AssignAddressForm(request.POST,vrf=vrf,address_id=address_id)
            if form.is_valid():
                assert is_ipv4(form.cleaned_data["ip"])
                assert is_fqdn(form.cleaned_data["fqdn"])
                if not IPv4BlockAccess.check_write_access(request.user,vrf,form.cleaned_data["ip"]+"/32"):
                    return self.response_forbidden("Permission denied")
                if ip:
                    address.fqdn=form.cleaned_data["fqdn"]
                    address.ip=form.cleaned_data["ip"]
                    address.description=form.cleaned_data["description"]
                    address.tt=form.cleaned_data["tt"]
                    status="changed"
                else:
                    # Check no duplicated IPs
                    if IPv4Address.objects.filter(vrf=vrf,ip=form.cleaned_data["ip"]).count()>0:
                        return render_failure(request,"Duplicated IP address","Address %s is already present in VRF %s"%(form.cleaned_data["ip"],vrf.name))
                    address=IPv4Address(vrf=vrf,fqdn=form.cleaned_data["fqdn"],
                        ip=form.cleaned_data["ip"],description=form.cleaned_data["description"],
                        modified_by=request.user)
                    status="created"
                address.save()
                self.message_user(request,"IP Address %s in VRF %s %s successfully"%(form.cleaned_data["ip"],str(vrf),status))
                return self.response_redirect("%s%d/%s/"%(self.base_url,vrf.id,address.parent.prefix))
        else:
            if "ip" not in initial:
                # Try to calculate ip address from referer
                referer=request.META.get("HTTP_REFERER",None)
                if referer:
                    match=rx_url_cidr.match(referer)
                    if match and is_cidr(match.group(1)):
                        block=match.group(1)
                        # Find first free IP address
                        c=self.cursor()
                        c.execute("SELECT free_ip(%s,%s)",[vrf.id,block])
                        ip=c.fetchall()[0][0]
                        if ip:
                            initial["ip"]=ip
                        else:
                            initial["ip"]="NO FREE IP"
            form=self.AssignAddressForm(initial=initial)
        return self.render(request,"assign_address.html",{"vrf":vrf,"form":form,"p":p,"parents":parents})
    view_assign_address.url=[
        URL(r"^(?P<vrf_id>\d+)/assign_address/$",name="assign_address"),
        URL(r"^(?P<vrf_id>\d+)/(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3})/assign_address/$",name="change_address"),
        URL(r"^(?P<vrf_id>\d+)/(?P<new_ip>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3})/assign_address/new/$",name="assign_new_address")
    ]
    view_assign_address.access=Application.has_perm("ip.change_ipv4block")
    ##
    ## Deallocate ip address handler
    ##
    def view_revoke_address(self,request,vrf_id,ip):
        assert is_ipv4(ip)
        vrf_id=int(vrf_id)
        vrf=get_object_or_404(VRF,id=vrf_id)
        address=get_object_or_404(IPv4Address,vrf=vrf,ip=ip)
        if not IPv4BlockAccess.check_write_access(request.user,vrf,ip+"/32"):
            return self.response_forbidden("Permission denied")
        address.delete()
        self.message_user(request,"IP address %s in VRF %s successfully deleted"%(ip,str(vrf)))
        return self.response_redirect("%s%d/%s/"%(self.base_url,vrf.id,address.parent.prefix))
    view_revoke_address.url=r"^(?P<vrf_id>\d+)/(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/revoke_address/$"
    view_revoke_address.url_name="revoke_address"
    view_revoke_address.access=Application.has_perm("ip.change_ipv4block")
    ##
    ## Bind VC to Prefix
    ##
    def view_bind_vc(self,request,vrf_id,prefix):
        def get_bind_vc_form(prefix):
            class BindVCForm(forms.Form):
                vc=forms.ChoiceField(label="VC",choices=VCBindFilter.get_choices(prefix),required=True)
            return BindVCForm
        vrf=get_object_or_404(VRF,id=int(vrf_id))
        p=get_object_or_404(IPv4Block,vrf=vrf,prefix=prefix)
        if not IPv4BlockAccess.check_write_access(request.user,vrf,prefix):
            return self.response_forbidden("Permission denied")
        initial={"vc":p.vc}
        if request.POST:
            form=get_bind_vc_form(p)(request.POST,initial=initial)
            if form.is_valid():
                # Bind to vc
                p.vc=get_object_or_404(VC,id=form.cleaned_data["vc"])
                p.save()
                self.message_user(request,"Prefix %s is succesfully bind to VC %s"%(prefix,str(p.vc)))
                return self.response_redirect("%s%d/%s/"%(self.base_url,vrf.id,prefix))
        else:
            form=get_bind_vc_form(p)(initial=initial)
        return self.render(request,"bind_vc.html",{"form":form,"prefix":p})
    view_bind_vc.url=r"(?P<vrf_id>\d+)/(?P<prefix>\S+)/bind_vc/$"
    view_bind_vc.url_name="bind_vc"
    view_bind_vc.access=Application.has_perm("ip.change_ipv4block")
