from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils.simplejson.encoder import JSONEncoder

def render(request,template,dict={}):
    return render_to_response(template,dict,context_instance=RequestContext(request))

def render_plain_text(text):
    return HttpResponse(text,mimetype="text/plain")
    
def render_json(obj):
    return HttpResponse(JSONEncoder(ensure_ascii=False).encode(obj),mimetype="text/json")
    