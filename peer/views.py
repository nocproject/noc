from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseForbidden

from noc.peer.models import AS
from noc.lib.render import render
from noc.lib.validators import is_asn

def index(request):
    ases=AS.objects.all()
    return render(request,"peer/index.html",{"ases":ases})
    
def rpsl(request,asn):
    assert is_asn(asn)
    asn=get_object_or_404(AS,asn=int(asn))
    return render(request,"peer/rpsl.html",{"asn":asn})
