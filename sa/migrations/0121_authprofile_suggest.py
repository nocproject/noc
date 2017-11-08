from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        # Mock Models
        AuthProfile = db.mock_model(
            model_name="AuthProfile",
            db_table="sa_authprofile", db_tablespace="",
            pk_field_name="id", pk_field_type=models.AutoField)
        #
        db.create_table("sa_authprofilesuggestsnmp", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("auth_profile", models.ForeignKey(AuthProfile)),
            ("snmp_ro", models.CharField("RO Community", blank=True, null=True, max_length=64)),
            ("snmp_rw", models.CharField("RW Community", blank=True, null=True, max_length=64))
        ))
        db.create_table("sa_authprofilesuggestcli", (
            ("id", models.AutoField(verbose_name="ID", primary_key=True, auto_created=True)),
            ("auth_profile", models.ForeignKey(AuthProfile)),
            ("user", models.CharField("User", max_length=32, blank=True, null=True)),
            ("password", models.CharField("Password", max_length=32, blank=True, null=True)),
            ("super_password", models.CharField("Super Password", max_length=32, blank=True, null=True))
        ))

    def backwards(self):
        pass
