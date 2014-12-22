# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AuditTrail model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import datetime
## Django modules
from django.db.models import signals as django_signals
from django.utils.encoding import smart_unicode
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, DateTimeField,
                                ListField, EmbeddedDocumentField)
## NOC modules
from noc.lib.middleware import get_user
from noc import settings
from noc.lib.utils import get_model_id
from noc.lib.text import to_seconds

logger = logging.getLogger(__name__)


class FieldChange(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    field = StringField()
    old = StringField(required=False)
    new = StringField(required=False)

    def __unicode__(self):
        return self.field


class AuditTrail(Document):
    meta = {
        "collection": "noc.audittrail",
        "allow_inheritance": False,
        "indexes": [
            "timestamp",
            ("model_id", "object"),
            {
                "fields": ["expires"],
                "expireAfterSeconds": 0
            }
        ]
    }

    timestamp = DateTimeField()
    user = StringField()
    model_id = StringField()
    object = StringField()
    op = StringField(
        choices=[
            ("C", "Create"),
            ("M", "Modify"),
            ("D", "Delete")
        ]
    )
    changes = ListField(EmbeddedDocumentField(FieldChange))
    expires = DateTimeField()

    EXCLUDE = set([
        "admin.logentry",
        "main.audittrail",
        "kb.kbentryhistory",
        "kb/kbentrypreviewlog",
        "sa.maptask",
        "sa.reducetask",
    ])

    DEFAULT_TTL = to_seconds(settings.config.get("audit", "ttl.db"))
    _model_ttls = {}

    @classmethod
    def log(cls, sender, instance, op, changes):
        """
        Log into audit trail
        """
        user = get_user()  # Retrieve user from thread local storage
        if not user or not user.is_authenticated():
            return  # No user initialized, no audit trail
        if not changes:
            logger.debug("Nothing to log for %s", instance)
            return
        now = datetime.datetime.now()
        model_id = get_model_id(sender)
        cls._get_collection().insert({
            "timestamp": now,
            "user": user.username,
            "model_id": model_id,
            "object": str(instance.pk),
            "op": op,
            "changes": changes,
            "expires": now + cls._model_ttls[model_id]
        }, w=0)

    @classmethod
    def get_field(cls, instance, field):
        if field._get_val_from_obj(instance) is None:
            return None
        else:
            return field.value_to_string(instance)

    @classmethod
    def on_update_model(cls, sender, instance, **kwargs):
        """
        Audit trail for INSERT and UPDATE operations
        """
        #
        logger.debug("Logging change for %s", instance)
        changes = []
        if instance.pk:
            # Update
            op = "U"
            for f in sender._meta.fields:
                od = instance._old_values.get(f.attname)
                if od is not None:
                    od = smart_unicode(od)
                nd = cls.get_field(instance, f)
                if nd != od:
                    changes += [{
                        "field": f.name,
                        "old": od,
                        "new": nd
                    }]
        else:
            # Create
            op = "C"
            changes = [{
                "field": f.name,
                "old": None,
                "new": cls.get_field(instance, f)
            } for f in sender._meta.fields]
        cls.log(sender, instance, op, changes)

    @classmethod
    def on_delete_model(cls, sender, instance, **kwargs):
        """
        Audit trail for DELETE operation
        """
        #
        logger.debug("Logging deletion of %s", instance)
        changes = [{
            "field": f.name,
            "old": cls.get_field(instance, f),
            "new": None
        } for f in sender._meta.fields]
        cls.log(sender, instance, "D", changes)

    @classmethod
    def on_init_model(cls, sender, instance, **kwargs):
        """
        Preserve original values
        """
        instance._old_values = dict(instance.__dict__)

    @classmethod
    def get_model_ttl(cls, model_id):
        m = model_id.split(".")[0]
        if settings.config.has_option("audit", "ttl.db.%s" % model_id):
            v = to_seconds(settings.config.get("audit", "ttl.db.%s" % model_id))
        elif settings.config.has_option("audit", "ttl.db.%s" % m):
            v = to_seconds(settings.config.get("audit", "ttl.db.%s" % m))
        else:
            v = cls.DEFAULT_TTL
        return datetime.timedelta(seconds=v)

    @classmethod
    def on_new_model(cls, sender, **kwargs):
        if str(sender._meta) in cls.EXCLUDE:
            return  # Ignore model
        model_id = get_model_id(sender)
        ttl = cls.get_model_ttl(model_id)
        if not ttl:
            return  # Disabled
        cls._model_ttls[model_id] = ttl
        django_signals.post_save.connect(cls.on_update_model,
                                         sender=sender)
        django_signals.post_delete.connect(cls.on_delete_model,
                                           sender=sender)
        django_signals.post_init.connect(cls.on_init_model,
                                         sender=sender)

    @classmethod
    def install(cls):
        """
        Install signal handlers
        """
        if settings.IS_WEB:
            django_signals.class_prepared.connect(cls.on_new_model)
