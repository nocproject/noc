from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseForbidden

from noc.dns.models import DNSZone
from noc.lib.render import render


def index(request,zonetype="F"):
    assert zonetype in ["F","R"]
    zones=[z for z in DNSZone.objects.order_by("name") if z.type==zonetype]
    return render(request,"dns/index.html",{"zones":zones,"zonetype":zonetype})
    