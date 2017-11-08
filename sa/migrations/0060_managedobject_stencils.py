from django.db import models
from south.db import db


class Migration:
    def forwards(self):
        db.add_column("sa_managedobjectprofile",
                      "shape",
                      models.CharField(_("Shape"), blank=True, null=True,
                                       max_length=128))
        db.add_column("sa_managedobject",
                      "shape",
                      models.CharField(_("Shape"), blank=True, null=True,
                                       max_length=128))

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "shape")
        db.delete_column("sa_managedobject", "shape")
