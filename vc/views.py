# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django's standard views module
## For VC application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.shortcuts import get_object_or_404
from django import forms
from django.contrib.auth.decorators import permission_required
from noc.lib.render import render,render_success
from noc.vc.models import VCDomain,VCFilter,VC,VCType
from noc.sa.models import ManagedObject, profile_registry
from noc.settings import config
from xmlrpclib import ServerProxy, Error

##
## Profiles having get_vlans script
##
get_vlans_profiles=[p.name for p in profile_registry.classes.values() if "get_vlans" in p.scripts]
##
## Test VC Filter
##
class VCFilterTestForm(forms.Form):
    vc_id=forms.IntegerField(label="VC Id",required=False)
    vc_domain=forms.ModelChoiceField(label="OR VC Domain",queryset=VCDomain.objects,required=False)

@permission_required("vc.add_vcfilter")
def vc_filter_test(request,filter_id):
    vc_filter=get_object_or_404(VCFilter,id=int(filter_id))
    result=[]
    if request.POST:
        form=VCFilterTestForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["vc_id"]:
                vcs=[(form.cleaned_data["vc_id"],"Test")]
            elif form.cleaned_data["vc_domain"]:
                vcs=[(v.l1,v.name) for v in form.cleaned_data["vc_domain"].vc_set.order_by("l1")]
            result=[v for v in vcs if vc_filter.check(v[0])]
    else:
        form=VCFilterTestForm()
    return render(request,"vc/vc_filter_test.html",{"form":form,"vc_filter":vc_filter,"result":result})
##
## Import vlans from switches via SA
##
class SAImportVLANsForm(forms.Form):
    vc_domain=forms.ModelChoiceField(label="VC Domain",queryset=VCDomain.objects)
    managed_object=forms.ModelChoiceField(label="Managed Object",queryset=ManagedObject.objects.filter(profile_name__in=get_vlans_profiles))

@permission_required("vc.add_vc")
def sa_import_vlans(request):
    def update_vlans(vc_domain,mo):
        script="%s.get_vlans"%mo.profile_name
        count=0
        server=ServerProxy("http://%s:%d"%(config.get("xmlrpc","server"),config.getint("xmlrpc","port")))
        result=server.script(script,mo.id,{})
        for v in result:
            vlan_id=v["vlan_id"]
            name=v.get("name","VLAN%d"%vlan_id)
            try:
                vc=VC.objects.get(vc_domain=vc_domain,l1=vlan_id)
            except VC.DoesNotExist:
                vc=VC(vc_domain=vc_domain,l1=vlan_id,l2=0,name=name,description=name)
                vc.save()
                count+=1
        return count
    if request.POST:
        form=SAImportVLANsForm(request.POST)
        if form.is_valid():
            count=update_vlans(form.cleaned_data["vc_domain"],form.cleaned_data["managed_object"])
            return render_success(request,"VLANs are imported","%d VLANs are imported"%count)
    else:
        form=SAImportVLANsForm()
    return render(request,"vc/sa_import_vlans.html",{"form":form})
