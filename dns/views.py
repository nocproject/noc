from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseForbidden
from noc.dns.models import DNSZone,DNSServer
from noc.lib.render import render,render_plain_text

def zone(request,zone,ns_id):
    z=get_object_or_404(DNSZone,name=zone)
    ns=get_object_or_404(DNSServer,id=int(ns_id))
    return render_plain_text(z.zonedata(ns))
