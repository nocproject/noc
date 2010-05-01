# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## KBGlobalBookmark Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.kb.models import KBGlobalBookmark
##
## KBGlobalBookmark admin
##
class KBGlobalBookmarkAdmin(admin.ModelAdmin):
    list_display=["kb_entry"]
##
## KBGlobalBookmark application
##
class KBGlobalBookmarkApplication(ModelApplication):
    model=KBGlobalBookmark
    model_admin=KBGlobalBookmarkAdmin
    menu="Setup | Global Bookmark"
