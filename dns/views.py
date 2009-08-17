# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseForbidden
from django import forms
from noc.dns.models import DNSZone,DNSServer, DNSZoneProfile
from noc.lib.render import render,render_plain_text,render_success
from noc.lib.validators import is_fqdn
from noc.sa.models import TaskSchedule
import datetime

def zone(request,zone,ns_id):
    z=get_object_or_404(DNSZone,name=zone)
    ns=get_object_or_404(DNSServer,id=int(ns_id))
    return render_plain_text(z.zonedata(ns))

def zone_rpsl(request,zone):
    z=get_object_or_404(DNSZone,name=zone)
    return render_plain_text(z.rpsl)
##
## Upload Zones
##
class ZonesUploadForm(forms.Form):
    profile=forms.ModelChoiceField(queryset=DNSZoneProfile.objects)
    file=forms.FileField()

def upload_zones(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access Denied")
    if request.method=="POST":
        form = ZonesUploadForm(request.POST, request.FILES)
        if form.is_valid():
            profile=form.cleaned_data["profile"]
            n=0
            # Create missed records
            for l in request.FILES["file"].read().split("\n"):
                l=l.strip().lower()
                if not l or not is_fqdn(l):
                    continue
                try:
                    DNSZone.objects.get(name=l)
                    continue # Skip existing zones
                except DNSZone.DoesNotExist:
                    pass
                DNSZone(name=l,is_auto_generated=False,profile=profile).save()
                n+=1
            if n==0:
                return render_success(request,"No new zones found")
            else:
                # Trigger dns.update_domain_expiration to update paid_till
                try:
                    t=TaskSchedule.objects.get(periodic_name="dns.update_domain_expiration")
                    t.next_run=datetime.datetime.now()+datetime.timedelta(minutes=10)
                    t.save()
                except TaskSchedule.DoesNotExist:
                    pass
                return render_success(request,"%d new zones are imported"%n)
    return HttpResponseRedirect("/dns/tools/")
##
## Tools page
##
def tools(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access Denied")
    return render(request,"dns/tools.html",{"zones_upload_form":ZonesUploadForm()})
