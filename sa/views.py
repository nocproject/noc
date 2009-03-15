# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.shortcuts import get_object_or_404
from noc.lib.render import render, render_failure
from noc.sa.models import ManagedObject,script_registry,profile_registry
from django.http import HttpResponseForbidden,HttpResponseNotFound
from xmlrpclib import ServerProxy, Error
from noc.settings import config
import pprint,types,socket

def object_scripts(request,object_id):
    o=get_object_or_404(ManagedObject,id=int(object_id))
    if not o.has_access(request.user):
        return HttpResponseForbidden("Access denied")
    p=o.profile_name
    scripts=sorted([(p+"."+x,x) for x in profile_registry[p].scripts.keys()])
    return render(request,"sa/scripts.html",{"object":o,"scripts":scripts})

def object_script(request,object_id,script):
    def get_result(script,object_id,**kwargs):
        server=ServerProxy("http://%s:%d"%(config.get("xmlrpc","server"),config.getint("xmlrpc","port")))
        try:
            result=server.script(script,object_id,kwargs)
        except socket.error,why:
            raise Exception("XML-RPC socket error: "+why[1])
        if type(result) not in [types.StringType,types.UnicodeType]:
            result=pprint.pformat(result)
        return result
        
    o=get_object_or_404(ManagedObject,id=int(object_id))
    if not o.has_access(request.user):
        return HttpResponseForbidden("Access denied")
    try:
        scr=script_registry[script]
    except:
        return HttpResponseNotFound("No script found")
    form=None
    result=None
    if scr.implements and scr.implements[0].requires_input():
        if request.POST:
            form=scr.implements[0].get_form(request.POST)
            if form.is_valid():
                data={}
                for k,v in form.cleaned_data.items():
                    if v:
                        data[k]=v
                try:
                    result=get_result(script,object_id,**data)
                except Exception,why:
                    return render_failure(request,"Script Failed",why)
        else:
            form=scr.implements[0].get_form()
    else:
        try:
            result=get_result(script,object_id)
        except Exception,why:
            return render_failure(request,"Script Failed",why)
    return render(request,"sa/script.html",{"object":o,"result":result,"script":script,"form":form})
