from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseForbidden,HttpResponse
from django import forms

from noc.peer.models import AS,ASSet,LGQueryType,PeeringPoint,LGQueryCommand
from noc.sa.models import Task
from noc.lib.render import render,render_plain_text,render_json
from noc.lib.validators import is_asn,is_as_set,is_ipv4,is_cidr
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
    def clean_query(self):
        peering_point = self.cleaned_data.get("peering_point", None)
        query_type = self.cleaned_data.get("query_type", None)
        query = self.cleaned_data.get("query", "").strip()
        if peering_point and query_type:
            try:
                qc=LGQueryCommand.objects.get(profile_name=peering_point.profile_name,query_type=query_type)
            except LGQueryCommand.DoesNotExist:
                raise forms.ValidationError("Query type is not supported for this router")
            if query=="" and qc.is_argument_required:
                raise forms.ValidationError("Missed query argument")
            if not is_ipv4(query) and not is_cidr(query):
                raise forms.ValidationError("Invalid query")
        return query
    
def lg(request):
    task_id=None
    if request.POST:
        form=LGForm(request.POST)
        if form.is_valid():
            pp=form.cleaned_data["peering_point"]
            cmd=pp.lg_command(form.cleaned_data["query_type"],form.cleaned_data["query"])
            task_id=Task.create_task(
                pp.profile_name,
                pp.lg_rcmd,
                "sa.actions.cli",
                args={"commands":[cmd]},
                timeout=60
            )
    else:
        form=LGForm()
    return render(request,"peer/lg.html",{"form":form,"task_id":task_id})
    
def lg_json(request,task_id):
    t=get_object_or_404(Task,task_id=int(task_id))
    # Format output
    out=t.out
    profile=t.profile
    if profile.pattern_lg_as_path_list:
        rx=re.compile(profile.pattern_lg_as_path_list,re.DOTALL|re.MULTILINE)
        out=rx.sub(profile.lg_as_path,out)
    if profile.pattern_lg_best_path:
        rx=re.compile(profile.pattern_lg_best_path,re.DOTALL|re.MULTILINE)
        out=rx.sub(r"<span style='color: red'>\1</span>",out)
    r={
        "status" : t.status,
        "out"    : out,
    }
    # Remove complete and failed queries
    if t.status in ["c","f"]:
        t.delete()
    return render_json(r)