from noc.cm.models import Object
from django.shortcuts import get_object_or_404
from noc.lib.render import render,render_plain_text
import os

def view(request,object_id):
    o=get_object_or_404(Object,id=int(object_id))
    return render(request,"cm/view.html",{"o":o})
    
def text(request,object_id):
    o=get_object_or_404(Object,id=int(object_id))
    return render_plain_text(o.data)