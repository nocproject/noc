from noc.cm.models import Object
from django.shortcuts import get_object_or_404
from noc.lib.render import render,render_plain_text
import os
from django.http import HttpResponseNotFound

def view(request,object_id,revision=None,format="html"):
    o=get_object_or_404(Object,id=int(object_id))
    if revision:
        r=None
        for rev in o.revisions:
            if rev.revision==revision:
                r=rev
                break
        if not r:
            return HttpResponseNotFound("Revision not found")
    else:
        r=o.revisions[0]
    content=o.get_revision(r)
    if format=="html":
        return render(request,"cm/view.html",{"o":o,"r":r,"content":content})
    elif format=="text":
        return render_plain_text(content)
    else:
        return HttpResponseNotFound("Invalid format: %s"%format)