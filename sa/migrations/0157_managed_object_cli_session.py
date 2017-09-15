from south.db import db
from django.db import models


class Migration:
    def forwards(self):
        # Profile settings
        db.add_column(
            "sa_managedobjectprofile",
            "cli_session_policy",
            models.CharField(
                "CLI Session Policy",
                max_length=1,
                choices=[
                    ("E", "Enable"),
                    ("D", "Disable")
                ],
                default="E"
            )
        )
        # Object settings
        db.add_column(
            "sa_managedobject",
            "cli_session_policy",
            models.CharField(
                "CLI Session Policy",
                max_length=1,
                choices=[
                    ("E", "Enable"),
                    ("D", "Disable"),
                    ("P", "From Profile")
                ],
                default="P"
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile",
                         "cli_session_policy")
        db.delete_column("sa_managedobject",
                         "cli_session_policy")
