from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        ManagedObjectProfile = db.mock_model(
            model_name="ManagedObjectProfile",
            db_table="sa_managedobjectprofile",
            db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        AuthProfile = db.mock_model(
            model_name="AuthProfile",
            db_table="sa_authprofile",
            db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        db.add_column(
            "sa_managedobjectprofile",
            "cpe_profile",
            models.ForeignKey(
                ManagedObjectProfile,
                verbose_name="Object Profile",
                blank=True, null=True
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "cpe_auth_profile",
            models.ForeignKey(
                AuthProfile,
                verbose_name="Object Profile",
                blank=True, null=True
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile",
                         "cpe_profile_id")
        db.delete_column("sa_managedobjectprofile",
                         "cpe_auth_profile_id")
