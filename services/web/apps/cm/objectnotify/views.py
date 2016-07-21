# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectNotify Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app.modelapplication import ModelApplication
from noc.cm.models import ObjectNotify
from noc.core.translation import ugettext as _
##
## ObjectNotify admin
##
class ObjectNotifyAdmin(admin.ModelAdmin):
    list_display=["type","administrative_domain","notify_immediately","notify_delayed","notification_group"]
    list_filter=["type","administrative_domain","notification_group"]
##
## ObjectNotify application
##
class ObjectNotifyApplication(ModelApplication):
    model=ObjectNotify
    model_admin=ObjectNotifyAdmin
    menu = [_("Setup"), _("Object Notifies")]
