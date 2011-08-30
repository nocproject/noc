# encoding: utf-8
import datetime
from south.db import db
from django.db import models
from noc.main.models import *

class Migration:

    def forwards(self):
        # Model 'Color'
        db.create_table('main_style', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=64,unique=True)),
            ('font_color', ColorField("Font Color",default=0x000000)),
            ('background_color', ColorField("Background Color",default=0xffffff)),
            ('bold', models.BooleanField('Bold', default=False)),
            ('italic', models.BooleanField('Italic', default=False)),
            ('underlined', models.BooleanField('Underlined', default=False)),
            ('is_active', models.BooleanField("Is Active",default=True)),
            ('description', models.TextField("Description",null=True,blank=True)),
        ))

    def backwards(self):
        db.delete_table("main_style")
