from django.shortcuts import get_object_or_404
from noc.lib.render import render
from noc.fm.models import Event,EventData

def index(request):
    events=Event.objects.order_by("-id")
    return render(request,"fm/index.html",{"events":events})

def event(request,event_id):
    event=get_object_or_404(Event,id=int(event_id))
    return render(request,"fm/event.html",{"e":event})
