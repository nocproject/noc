# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
"""
"""
import datetime
from south.db import db
<<<<<<< HEAD
from django.db import models
=======
from noc.fm.models import *
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

class Migration:
    def forwards(self):
        db.delete_table("fm_eventrepeat")
        db.delete_table("fm_eventlog")
        db.delete_table("fm_eventdata")
        db.delete_table("fm_event")
        db.delete_table("fm_mibdata")
        db.delete_table("fm_mibdependency")
        db.delete_table("fm_mib")
        db.delete_table("fm_eventpriority")
        db.delete_table("fm_eventpostprocessingre")
        db.delete_table("fm_eventpostprocessingrule")
        db.delete_table("fm_eventcorrelationmatchedvar")
        db.delete_table("fm_eventcorrelationmatchedclass")
        db.delete_table("fm_eventclassificationre")
        db.delete_table("fm_eventclassificationrule")
        db.delete_table("fm_eventclassvar")
        db.delete_table("fm_eventclass")
        db.delete_table("fm_eventcategory")
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        pass
