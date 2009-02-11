# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseForbidden
from noc.dns.models import DNSZone,DNSServer
from noc.lib.render import render,render_plain_text

def zone(request,zone,ns_id):
    z=get_object_or_404(DNSZone,name=zone)
    ns=get_object_or_404(DNSServer,id=int(ns_id))
    return render_plain_text(z.zonedata(ns))

def zone_rpsl(request,zone):
    z=get_object_or_404(DNSZone,name=zone)
    return render_plain_text(z.rpsl)
