# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from django.db import models
import os,stat,datetime

TYPES={
    "config":"config",
    "prefixlist":"prefix-list",
    "dns":"dns",
    "rpsl":"rpsl",
    }

class Migration: 
    def forwards(self):
        for ot in TYPES:
            db.add_column("cm_%s"%ot,"last_modified",models.DateTimeField("Last Modified",blank=True,null=True))

    def backwards(self):
        for ot in TYPES:
            db.delete_column("cm_%s"%ot,"last_modified")
