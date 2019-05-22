# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# access and notify
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.migration.base import BaseMigration

OBJECT_TYPES = ["config", "dns", "prefixlist", "rpsl"]
OBJECT_TYPE_CHOICES = [(x, x) for x in OBJECT_TYPES]


class Migration(BaseMigration):
    def migrate(self):

        self.db.delete_column("cm_objectcategory", "notify_immediately")
        self.db.delete_column("cm_objectcategory", "notify_delayed")

        self.db.create_table(
            'cm_objectlocation', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField("Name", max_length=64, unique=True)),
                ('description', models.CharField("Description", max_length=128, null=True, blank=True))
            )
        )

        ObjectLocation = self.db.mock_model(
            model_name='ObjectLocation',
            db_table='cm_objectlocation',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )

        self.db.execute("INSERT INTO cm_objectlocation(name,description) values(%s,%s)", ["default", "default location"])
        loc_id = self.db.execute("SELECT id FROM cm_objectlocation WHERE name=%s", ["default"])[0][0]

        for ot in OBJECT_TYPES:
            self.db.add_column("cm_%s" % ot, "location", models.ForeignKey(ObjectLocation, null=True, blank=True))
            self.db.execute("UPDATE cm_%s SET location_id=%%s" % ot, [loc_id])
            self.db.execute("ALTER TABLE cm_%s ALTER location_id SET NOT NULL" % ot)

        # Mock Models
        ObjectCategory = self.db.mock_model(
            model_name='ObjectCategory',
            db_table='cm_objectcategory',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        ObjectLocation = self.db.mock_model(
            model_name='ObjectLocation',
            db_table='cm_objectlocation',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        User = self.db.mock_model(
            model_name='User',
            db_table='auth_user',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )

        # Model 'ObjectAccess'
        self.db.create_table(
            'cm_objectaccess', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('type', models.CharField("Type", max_length=16, choices=OBJECT_TYPE_CHOICES)),
                ('category', models.ForeignKey(ObjectCategory, verbose_name="Category", blank=True, null=True)),
                ('location', models.ForeignKey(ObjectLocation, verbose_name="Location", blank=True, null=True)),
                ('user', models.ForeignKey(User, verbose_name=User))
            )
        )

        # Mock Models
        ObjectCategory = self.db.mock_model(
            model_name='ObjectCategory',
            db_table='cm_objectcategory',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        ObjectLocation = self.db.mock_model(
            model_name='ObjectLocation',
            db_table='cm_objectlocation',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )

        # Model 'ObjectNotify'
        self.db.create_table(
            'cm_objectnotify', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('type', models.CharField("Type", max_length=16, choices=OBJECT_TYPE_CHOICES)),
                ('category', models.ForeignKey(ObjectCategory, verbose_name="Category", blank=True, null=True)),
                ('location', models.ForeignKey(ObjectLocation, verbose_name="Location", blank=True, null=True)),
                ('emails', models.CharField("Emails", max_length=128)),
                ('notify_immediately', models.BooleanField("Notify Immediately")),
                ('notify_delayed', models.BooleanField("Notify Delayed")),
            )
        )
