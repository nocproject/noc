# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Models for KB application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.kb.models import *
from noc.lib.render import render
from django.shortcuts import get_object_or_404

##
## Title page
##
def index(request):
    latest=[h.kb_entry for h in KBEntryHistory.objects.order_by("-timestamp")[:20]]
    return render(request,"kb/index.html",{"latest":latest})
##
## KB Entry Preview
##
def view(request,kb_id):
    e=get_object_or_404(KBEntry,id=int(kb_id))
    return render(request,"kb/view.html",{"e":e})
