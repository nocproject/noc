from django.template import RequestContext
from django.shortcuts import render_to_response

def render(request,template,dict={}):
    return render_to_response(template,dict,context_instance=RequestContext(request))