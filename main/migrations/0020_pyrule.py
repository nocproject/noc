# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# pyrule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db
from django.db import models


class Migration(object):
    def forwards(self):

        # Adding model 'PyRule'
        db.create_table(
            'main_pyrule', (
                ('id', models.AutoField(primary_key=True)),
                ('name', models.CharField("Name", unique=True, max_length=64)),
                ('interface', models.CharField("Interface", max_length=64)),
                ('description', models.TextField("Description")),
                ('text', models.TextField("Text")),
                ('changed', models.DateTimeField("Changed", auto_now=True, auto_now_add=True)),
            )
        )
        db.send_create_signal('main', ['PyRule'])

    def backwards(self):
        # Deleting model 'PyRule'
        db.delete_table('main_pyrule')
