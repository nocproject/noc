from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseForbidden,HttpResponse
from django import forms

from noc.peer.models import AS,ASSet,LGQueryType,PeeringPoint,LGQuery
from noc.lib.render import render,render_plain_text,render_json
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
    
##
## Looking glass
##
class LGForm(forms.Form):
    peering_point= forms.ModelChoiceField(queryset=PeeringPoint.objects.filter(lg_rcmd__isnull=False))
    query_type   = forms.ModelChoiceField(queryset=LGQueryType.objects.all())
    query        = forms.CharField()
    
def lg(request):
    q=None
    if request.POST:
        form=LGForm(request.POST)
        if form.is_valid():
            q=LGQuery.submit_query(request.META["REMOTE_ADDR"],form.cleaned_data["peering_point"],
                form.cleaned_data["query_type"],form.cleaned_data["query"])
            q.save()
    else:
        form=LGForm()
    return render(request,"peer/lg.html",{"form":form,"q":q})
    
def lg_json(request,query_id):
    q=get_object_or_404(LGQuery,query_id=int(query_id))
    r={
        "status" : q.status,
        "out"    : q.out,
    }
    return render_json(r)