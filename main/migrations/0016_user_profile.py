# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# user profile
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
        TimePattern = self.db.mock_model(
            model_name='TimePattern',
            db_table='main_timepattern',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        Language = self.db.mock_model(
            model_name='Language',
            db_table='main_language',
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
        # Adding model 'UserProfile'
        self.db.create_table(
            'main_userprofile', (
                ('id', models.AutoField(primary_key=True)),
                (
                    'preferred_language',
                    models.ForeignKey(Language, null=True, verbose_name="Preferred Language", blank=True)
                ),
                ('user', models.ForeignKey(User, unique=True)),
            )
        )
        UserProfile = self.db.mock_model(
            model_name='UserProfile',
            db_table='main_userprofile',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )

        # Adding model 'UserProfileContact'
        self.db.create_table(
            'main_userprofilecontact', (
                ('user_profile', models.ForeignKey(UserProfile, verbose_name="User Profile")),
                ('notification_method', models.CharField("Method", max_length=16)),
                ('params', models.CharField("Params", max_length=256)),
                ('time_pattern', models.ForeignKey(TimePattern, verbose_name="Time Pattern")),
                ('id', models.AutoField(primary_key=True)),
            )
        )
        # Creating unique_together for [user_profile, time_pattern, notification_method, params] on UserProfileContact.
        self.db.create_index(
            'main_userprofilecontact', ['user_profile_id', 'time_pattern_id', 'notification_method', 'params'],
            unique=True
        )
