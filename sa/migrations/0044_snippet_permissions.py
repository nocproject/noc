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
from south.db import db
from django.db import models


class Migration:
    def forwards(self):
        db.add_column("sa_commandsnippet", "permission_name",
                      models.CharField(_("Permission Name"), max_length=64,
                                       null=True, blank=True))
        db.add_column("sa_commandsnippet", "display_in_menu",
                      models.BooleanField(_("Show in menu"), default=False))
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.delete_column("sa_commandsnippet", "permission_name")
        db.delete_column("sa_commandsnippet", "display_in_menu")    
