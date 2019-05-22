# ----------------------------------------------------------------------
# managed object
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
        # Model 'AdministrativeDomain'
        self.db.create_table(
            'sa_administrativedomain', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField("Name", max_length=32, unique=True)),
                ('description', models.TextField("Description", null=True, blank=True))
            )
        )
        # Model 'ObjectGroup'
        self.db.create_table(
            'sa_objectgroup', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField("Name", max_length=32, unique=True)),
                ('description', models.TextField("Description", null=True, blank=True))
            )
        )

        # Mock Models
        AdministrativeDomain = self.db.mock_model(
            model_name='AdministrativeDomain',
            db_table='sa_administrativedomain',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        Activator = self.db.mock_model(
            model_name='Activator',
            db_table='sa_activator',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        self.db.create_table(
            'sa_managedobject', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField("Name", max_length=64, unique=True)),
                ('is_managed', models.BooleanField("Is Managed?", default=True)),
                ('administrative_domain', models.ForeignKey(AdministrativeDomain, verbose_name=AdministrativeDomain)),
                ('activator', models.ForeignKey(Activator, verbose_name=Activator)),
                ('profile_name', models.CharField("Profile", max_length=128)),
                ('scheme', models.IntegerField("Scheme")), ('address', models.CharField("Address", max_length=64)),
                ('port', models.PositiveIntegerField("Port", blank=True, null=True)),
                ('user', models.CharField("User", max_length=32, blank=True, null=True)),
                ('password', models.CharField("Password", max_length=32, blank=True, null=True)),
                ('super_password', models.CharField("Super Password", max_length=32, blank=True, null=True)),
                ('remote_path', models.CharField("Path", max_length=32, blank=True, null=True)),
                ('trap_source_ip', models.IPAddressField("Trap Source IP", null=True)),
                ('trap_community', models.CharField("Trap Community", blank=True, null=True, max_length=64)),
                ('is_configuration_managed', models.BooleanField("Is Configuration Managed?", default=True)),
                ('repo_path', models.CharField("Repo Path", max_length=128, blank=True, null=True))
            )
        )
        # Mock Models
        ManagedObject = self.db.mock_model(
            model_name='ManagedObject',
            db_table='sa_managedobject',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        ObjectGroup = self.db.mock_model(
            model_name='ObjectGroup',
            db_table='sa_objectgroup',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )

        # M2M field 'ManagedObject.groups'
        self.db.create_table(
            'sa_managedobject_groups', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('managedobject', models.ForeignKey(ManagedObject, null=False)),
                ('objectgroup', models.ForeignKey(ObjectGroup, null=False))
            )
        )

        # Mock Models
        User = self.db.mock_model(
            model_name='User',
            db_table='auth_user',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        AdministrativeDomain = self.db.mock_model(
            model_name='AdministrativeDomain',
            db_table='sa_administrativedomain',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )
        ObjectGroup = self.db.mock_model(
            model_name='ObjectGroup',
            db_table='sa_objectgroup',
            db_tablespace='',
            pk_field_name='id',
            pk_field_type=models.AutoField
        )

        # Model 'UserAccess'
        self.db.create_table(
            'sa_useraccess', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('user', models.ForeignKey(User, verbose_name=User)),
                (
                    'administrative_domain',
                    models.ForeignKey(
                        AdministrativeDomain, verbose_name="Administrative Domain", blank=True, null=True
                    )
                ),
                ('group', models.ForeignKey(ObjectGroup, verbose_name="Group", blank=True, null=True)),
            )
        )
