# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# systemnotification
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        NotificationGroup = self.db.mock_model(
            model_name='NotificationGroup',
            db_table='main_notificationgroup',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )

        # Adding model 'SystemNotification'
        self.db.create_table(
            'main_systemnotification', (
                (
                    'notification_group',
                    models.ForeignKey(NotificationGroup, null=True, verbose_name="Notification Group", blank=True)
                ),
                ('id', models.AutoField(primary_key=True)),
                ('name', models.CharField("Name", unique=True, max_length=64)),
            )
        )
