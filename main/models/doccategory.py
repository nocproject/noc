# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Common document category
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ObjectIdField
from mongoengine import signals


class DocCategory(Document):
    meta = {
        "collection": "noc.doccategories",
        "allow_inheritance": False,
        "indexes": ["type"]
    }

    name = StringField()
    type = StringField()
    parent = ObjectIdField()

    _senders = {}

    def __unicode__(self):
        return self.name

    @classmethod
    def register(cls, document):
        """
        Register document to category
        """
        cls._senders[document] = document._meta["collection"]
        signals.pre_save.connect(DocCategory.update_category,
                                 sender=document)

    @classmethod
    def update_category(cls, sender, document):
        """
        Update document category when necessary
        """
        type = cls._senders[sender]
        c_name = " | ".join(document.name.split(" | ")[:-1])
        c = DocCategory.objects.filter(type=type, name=c_name).first()
        if not c:
            c = DocCategory(type=type, name=c_name)
            c.save()
        document.category = c.id

    @classmethod
    def update_parent(cls, sender, document):
        if "|" in document.name:
            p_name = " | ".join(document.name.split(" | ")[:-1])
            p = DocCategory.objects.filter(
                type=document.type, name=p_name).first()
            if not p:
                # Create parent
                p = DocCategory(type=document.type, name=p_name)
                p.save()
            document.parent = p.id
        else:
            document.parent = None

    @classmethod
    def fix(cls, document):
        """
        Initialize categories structure
        """
        type = cls._senders[document]
        has_categories = bool(DocCategory.objects.filter(type=type).count())
        has_docs = bool(document.objects.count())
        if has_docs and not has_categories:
            for o in document.objects.all():
                o.save()

    @classmethod
    def fix_all(cls):
        for document in cls._senders:
            cls.fix(document)

## Set up signals
signals.pre_save.connect(DocCategory.update_parent, sender=DocCategory)
