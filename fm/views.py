from django.shortcuts import get_object_or_404
from noc.lib.render import render
from noc.fm.models import Event,EventData,EventClassificationRule,EventClassificationRE
from django.http import HttpResponseRedirect,HttpResponseForbidden
import random

def index(request):
    events=Event.objects.order_by("-id")
    return render(request,"fm/index.html",{"events":events})

def event(request,event_id):
    event=get_object_or_404(Event,id=int(event_id))
    return render(request,"fm/event.html",{"e":event})

def reclassify(request,event_id):
    event=get_object_or_404(Event,id=int(event_id))
    event.subject=None
    event.save()
    return HttpResponseRedirect("/fm/%d/"%event.id)

def create_rule(request,event_id):
    def re_q(s):
        return s.replace("\\","\\\\").replace(".","\\.").replace("+","\\+").replace("*","\\*")
    event=get_object_or_404(Event,id=int(event_id))
    rule=EventClassificationRule(event_class=event.event_class,name="Rule #%d:%d"%(event.id,random.randint(0,100000)),preference=1000)
    rule.save()
    for d in event.eventdata_set.filter(is_enriched=False):
        r=EventClassificationRE(rule=rule,left_re=re_q(d.key),right_re=re_q(d.value))
        r.save()
    return HttpResponseRedirect("/admin/fm/eventclassificationrule/%d/"%rule.id)