<<<<<<< HEAD
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ObjectModel model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
# Third-party modules
=======
## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectModel model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from mongoengine.document import Document
from mongoengine.fields import (StringField, ObjectIdField, FileField,
                                DateTimeField, IntField)
from mongoengine import signals
<<<<<<< HEAD
# NOC modules
=======
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from object import Object


class ObjectFile(Document):
    """
    Inventory object
    """
    meta = {
        "collection": "noc.objectfiles",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "indexes": ["object"]
    }

    object = ObjectIdField()
    name = StringField()
    file = FileField()
    ts = DateTimeField()
    description = StringField()
    size = IntField()
    mime_type = StringField()

    def __unicode__(self):
        return unicode(self.name or self.id)

    def delete_file(self):
        if self.file:
            self.file.delete()

    @classmethod
    def delete_files(cls, sender, document, target=None):
        for o in ObjectFile.objects.filter(object=document.id):
            o.delete_file()
            o.delete()

    @classmethod
    def on_delete(cls, sender, document, target=None):
        document.delete_file()


signals.pre_delete.connect(ObjectFile.delete_files, sender=Object)
signals.pre_delete.connect(ObjectFile.on_delete, sender=ObjectFile)
