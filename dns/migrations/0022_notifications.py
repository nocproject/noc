# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# notification
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
            model_name="NotificationGroup",
            db_table="main_notificationgroup",
            db_tablespace="",
            pk_field_name="id",
            pk_field_type=models.AutoField
        )
        self.db.add_column(
            "dns_dnszoneprofile", "notification_group", models.ForeignKey(NotificationGroup, blank=True, null=True)
        )
        self.db.add_column(
            "dns_dnszone", "notification_group", models.ForeignKey(NotificationGroup, blank=True, null=True))
