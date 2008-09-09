from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseForbidden
from noc.dns.models import DNSZone
from noc.lib.render import render,render_plain_text

def zone(request,zone):
    z=get_object_or_404(DNSZone,name=zone)
    return render_plain_text(z.zonedata)
