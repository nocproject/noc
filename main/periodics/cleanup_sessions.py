# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.periodic
from noc.settings import config
import os,subprocess,datetime
import logging

class Task(noc.sa.periodic.Task):
    name="main.cleanup_sessions"
    description=""
    
    def execute(self):
        from django.db import connection
        cursor=connection.cursor()
        cursor.execute("DELETE FROM django_session WHERE expire_date<'now'")
        cursor.execute("COMMIT")
        return True
