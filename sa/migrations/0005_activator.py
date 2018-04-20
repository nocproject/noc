# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from south.db import db


class Migration:

    def forwards(self):

        # Model 'Activator'
        db.create_table('sa_activator', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True)),
            ('ip', models.IPAddressField("IP")),
            ('auth', models.CharField("Auth String",max_length=64)),
            ('is_active', models.BooleanField("Is Active",default=True))
        ))

        db.send_create_signal('sa', ['Activator'])

    def backwards(self):
        db.delete_table('sa_activator')

