# ---------------------------------------------------------------------
# FM module database models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ObjectIdField


class AlarmClassCategory(Document):
    meta = {
        "collection": "noc.alartmclasscategories",  # @todo: Fix bug
        "strict": False,
        "auto_create_index": False,
    }
    name = StringField()
    parent = ObjectIdField(required=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if " | " in self.name:
            p_name = " | ".join(self.name.split(" | ")[:-1])
            p = AlarmClassCategory.objects.filter(name=p_name).first()
            if not p:
                p = AlarmClassCategory(name=p_name)
                p.save()
            self.parent = p.id
        else:
            self.parent = None
        super().save(*args, **kwargs)
