# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## User Group Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app import ModelApplication
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
##
##
##
class GroupApplication(ModelApplication):
    model=Group
    model_admin=GroupAdmin
    menu="Setup | Groups"
