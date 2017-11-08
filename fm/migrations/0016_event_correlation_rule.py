from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        # Model 'EventCorrelationRule'
        db.create_table('fm_eventcorrelationrule', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name", max_length=64, unique=True)),
            ('rule', models.TextField("Rule")),
            ('description', models.TextField("Description", null=True, blank=True)),
            ('is_builtin', models.BooleanField("Is Builtin", default=False))
        ))

        db.send_create_signal('fm', ['EventCorrelationRule'])

    def backwards(self):
        db.delete_table('fm_eventcorrelationrule')
