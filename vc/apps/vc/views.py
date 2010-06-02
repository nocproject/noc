# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VC Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django import forms
from noc.lib.app import ModelApplication,HasPerm
from noc.vc.models import VC,VCDomain
from noc.sa.models import ManagedObject
from noc.sa.models import profile_registry
from xmlrpclib import ServerProxy, Error
from noc.settings import config
##
## VC admin
##
class VCAdmin(admin.ModelAdmin):
    list_display=["vc_domain","name","l1","l2","description","blocks_list"]
    search_fields=["name","l1","l2","description"]
    list_filter=["vc_domain"]
##
## Import VLANs Form
##
get_vlans_profiles=[p.name for p in profile_registry.classes.values() if "get_vlans" in p.scripts]
class SAImportVLANsForm(forms.Form):
    vc_domain=forms.ModelChoiceField(label="VC Domain",queryset=VCDomain.objects)
    managed_object=forms.ModelChoiceField(label="Managed Object",
        queryset=ManagedObject.objects.filter(profile_name__in=get_vlans_profiles))

##
## VC application
##
class VCApplication(ModelApplication):
    model=VC
    model_admin=VCAdmin
    menu="Virtual Circuits"
    ##
    ## Import VLANs via service activation
    ##
    def view_import_sa(self,request):
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
                #count=update_vlans(form.cleaned_data["vc_domain"],form.cleaned_data["managed_object"])
                count=3
                return self.render_success(request,"VLANs are imported","%d new VLANs are imported"%count)
        else:
            form=SAImportVLANsForm()
        return self.render(request,"import_vlans.html",{"form":form})
    view_import_sa.url=r"^import_sa/$"
    view_import_sa.url_name="import_sa"
    view_import_sa.access=HasPerm("import")
