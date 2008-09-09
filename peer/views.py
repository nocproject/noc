from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseForbidden

from noc.peer.models import AS,ASSet
from noc.lib.render import render,render_plain_text
from noc.lib.validators import is_asn,is_as_set

def as_rpsl(request,asn):
    assert is_asn(asn)
    asn=get_object_or_404(AS,asn=int(asn))
    return render_plain_text(asn.rpsl)
    
def as_dot(request,asn):
    assert is_asn(asn)
    asn=get_object_or_404(AS,asn=int(asn))
    return render(request,"peer/as_dot.html",{"asn":asn})

def as_set_rpsl(request,as_set):
    assert is_as_set(as_set)
    as_set=get_object_or_404(ASSet,name=as_set)
    return render_plain_text(as_set.rpsl)