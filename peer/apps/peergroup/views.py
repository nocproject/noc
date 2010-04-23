# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PeerGroup Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.peer.models import PeerGroup
##
## PeerGroup admin
##
class PeerGroupAdmin(admin.ModelAdmin):
    list_display=["name","description","communities"]
##
## PeerGroup application
##
class PeerGroupApplication(ModelApplication):
    model=PeerGroup
    model_admin=PeerGroupAdmin
    menu="Setup | Peer Groups"
