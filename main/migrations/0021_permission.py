# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# permission
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
        # Adding model 'Permission'
        self.db.create_table(
            'main_permission', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField("Name", max_length=128, unique=True)),
            )
        )
        Permission = self.db.mock_model(
            model_name='Permission',
            db_table='main_permission',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )

        # Adding ManyToManyField 'Permission.groups'
        Group = self.db.mock_model(
            model_name='Group',
            db_table='auth_group',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        self.db.create_table(
            'main_permission_groups', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('permission', models.ForeignKey(Permission, null=False)),
                ('group', models.ForeignKey(Group, null=False))
            )
        )

        # Adding ManyToManyField 'Permission.users'
        User = self.db.mock_model(
            model_name='User',
            db_table='auth_user',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        self.db.create_table(
            'main_permission_users', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('permission', models.ForeignKey(Permission, null=False)),
                ('user', models.ForeignKey(User, null=False))
            )
        )
