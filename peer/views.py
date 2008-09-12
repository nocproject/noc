from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseForbidden,HttpResponse
from django import forms

from noc.peer.models import AS,ASSet,LGQueryType,PeeringPoint,LGQuery
from noc.lib.render import render,render_plain_text,render_json
from noc.lib.validators import is_asn,is_as_set
import re

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
    query        = forms.CharField(required=False)
    
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
        "out"    : LG_OUTPUT_FORMATTER[q.peering_point.type.name](q.out),
    }
    # Remove complete and failed queries
    if q.status in ["c","f"]:
        q.delete()
    return render_json(r)
##
## Output formatters for lg
##
def whois_formatter(q):
    return "<A HREF='http://www.db.ripe.net/whois?AS%s'>%s</A>"%(q,q)

rx_junos_as_path=re.compile("(?<=AS path: )(\d+(?: \d+)*)",re.MULTILINE|re.DOTALL)
rx_junos_best_path=re.compile(r"([+*]\[.*?\s> to \S+ via \S+)",re.MULTILINE|re.DOTALL)
def JUNOSOutputFormatter(s):
    def format_as_path_list(m):
        as_list=m.group(1).split()
        return " ".join([whois_formatter(x) for x in as_list])
    s=rx_junos_as_path.sub(format_as_path_list,s)
    s=rx_junos_best_path.sub(r"<span style='color: red'>\1</span>",s)
    return s

def IOSOutputFormatter(s):
    return s
    
LG_OUTPUT_FORMATTER={
    "IOS"   : IOSOutputFormatter,
    "JUNOS" : JUNOSOutputFormatter,
}