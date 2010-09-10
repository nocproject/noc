# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Obsolete data cleanup and system maintainance
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.periodic
from noc.settings import config
import os,subprocess,datetime
import logging
from tagging.models import TaggedItem

class Task(noc.sa.periodic.Task):
    name="main.cleanup"
    description="Obsolete data cleanup and system maintainance"
    
    def execute(self):
        from django.db import connection
        cursor=connection.cursor()
        # Delete expired sessions
        cursor.execute("DELETE FROM django_session WHERE expire_date<'now'")
        cursor.execute("COMMIT")
        # Find and delete hangling tags
        for i in TaggedItem.objects.all():
            if i.object is None:
                logging.info("Delete hanging tag reference: %s"%str(i))
                i.delete()
        cursor.execute("COMMIT")
        return True
