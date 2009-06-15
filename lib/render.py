# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HttpResponse wrappers and shortcuts
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils.simplejson.encoder import JSONEncoder
from noc.settings import config

##
## Setup Context Processor.
## Used via TEMPLATE_CONTEXT_PROCESSORS variable in settings.py
## Adds "setup" variable to context.
## "setup" is a hash of
##      "installation_name" 
##
def setup_processor(request):
    return {
        "setup" : {
            "installation_name" : config.get("customization","installation_name"),
            "logo_url"          : config.get("customization","logo_url"),
            "logo_width"        : config.get("customization","logo_width"),
            "logo_height"       : config.get("customization","logo_height"),
        }
    }
##
## Render template within context
##
def render(request,template,dict={}):
    return render_to_response(template,dict,context_instance=RequestContext(request))
##
## Create plain text response
##
def render_plain_text(text):
    return HttpResponse(text,mimetype="text/plain")
##
## Create serialized JSON-encoded response
##
def render_json(obj):
    return HttpResponse(JSONEncoder(ensure_ascii=False).encode(obj),mimetype="text/json")
##
## Render "success" page
##
def render_success(request,subject=None,text=None):
    return render(request,"main/success.html",{"subject":subject,"text":text})
##
## Render "failure" page
##
def render_failure(request,subject=None,text=None):
    return render(request,"main/failure.html",{"subject":subject,"text":text})
##
## Render wait page
##
def render_wait(request,subject=None,text=None,url=None,timeout=5):
    if url is None:
        url=request.path
    return render(request,"main/wait.html",{"subject":subject,"text":text,"timeout":timeout,"url":url})
