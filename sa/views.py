from django.shortcuts import get_object_or_404
from noc.lib.render import render
from noc.cm.models import Config
from noc.sa.models import script_registry
from django.http import HttpResponseForbidden
from xmlrpclib import ServerProxy, Error
from noc.settings import config
import pprint

def xmlrpc_server():
    return ServerProxy("http://%s:%d"%(config.get("xmlrpc","server"),config.getint("xmlrpc","port")))

def object_scripts(request,object_id):
    o=get_object_or_404(Config,id=int(object_id))
    if not o.has_access(request.user):
        return HttpResponseForbidden("Access denied")
    p=o.profile_name
    lp=len(p)+1
    scripts=[(x[0],x[0][lp:]) for x in script_registry.choices if x[0].startswith(p)]
    return render(request,"sa/scripts.html",{"object":o,"scripts":scripts})

def object_script(request,object_id,script):
    o=get_object_or_404(Config,id=int(object_id))
    if not o.has_access(request.user):
        return HttpResponseForbidden("Access denied")
    server=xmlrpc_server()
    result=server.script(script,object_id)
    result=pprint.pformat(result)
    return render(request,"sa/script.html",{"object":o,"result":result,"script":script})