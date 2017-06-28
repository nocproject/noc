# encoding: utf-8
from south.db import db
from django.db import models


class Migration:
    def forwards(self):

        # Adding model 'IgnoreEvents'
        db.create_table('fm_ignoreeventrules', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(unique=True, max_length=64)),
            ('left_re', models.CharField(max_length=256)),
            ('right_re', models.CharField(max_length=256)),
            ('is_active', models.BooleanField(default=True, blank=True)),
            ('description', models.TextField(null=True, blank=True)),
        ))
        db.send_create_signal('fm', ['IgnoreEventRules'])

    def backwards(self):
        # Deleting model 'IgnoreEvents'
        db.delete_table('fm_ignoreeventrules')
