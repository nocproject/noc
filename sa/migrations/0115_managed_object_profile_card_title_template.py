from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "card_title_template",
            models.CharField(
                _("Card title template"),
                max_length=256,
                default="{{ object.object_profile.name }}: {{ object.name }}"
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "card")
