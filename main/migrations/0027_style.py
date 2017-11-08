# encoding: utf-8
from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        # Model 'Color'
        db.create_table('main_style', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name", max_length=64, unique=True)),
            ('font_color', models.IntegerField("Font Color", default=0x000000)),
            ('background_color', models.IntegerField("Background Color", default=0xffffff)),
            ('bold', models.BooleanField('Bold', default=False)),
            ('italic', models.BooleanField('Italic', default=False)),
            ('underlined', models.BooleanField('Underlined', default=False)),
            ('is_active', models.BooleanField("Is Active", default=True)),
            ('description', models.TextField("Description", null=True, blank=True)),
        ))

    def backwards(self):
        db.delete_table("main_style")
