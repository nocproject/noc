# -*- coding: utf-8 -*-

# Third-party modules
from south.db import db
# NOC modules
from django.db import models


class Migration:
    depends_on = (
        ('sa', '0056_managedobjectselecter_filter_object_profile'),
    )

    def forwards(self):
        ManagedObjectSelector = db.mock_model(
            model_name="ManagedObjectSelector",
            db_table="sa_managedobjectselector", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)
        db.create_table('inv_networkchart', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name", max_length=64, unique=True)),
            ('description', models.TextField("Description", blank=True, null=True)),
            ('is_active', models.BooleanField("Is Active", default=True)),
            ('selector', models.ForeignKey(ManagedObjectSelector))
        ))

    def backwards(self):
        db.delete_table("inv_networkchart")
