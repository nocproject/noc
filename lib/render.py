from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

def render(request,template,dict={}):
    return render_to_response(template,dict,context_instance=RequestContext(request))

def render_plain_text(text):
    return HttpResponse(text,mimetype="text/plain")
    