# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AuditTrail model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Django modules
from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals as django_signals
## NOC modules
from noc.lib.middleware import get_user
from noc import settings

logger = logging.getLogger(__name__)


class AuditTrail(models.Model):
    """
    Audit Trail
    """
    class Meta:
        verbose_name = "Audit Trail"
        verbose_name_plural = "Audit Trail"
        db_table = "main_audittrail"
        app_label = "main"
        ordering = ["-timestamp"]

    user = models.ForeignKey(User, verbose_name="User")
    timestamp = models.DateTimeField("Timestamp", auto_now=True)
    model = models.CharField("Model", max_length=128)
    db_table = models.CharField("Table", max_length=128)
    operation = models.CharField(
        "Operation", max_length=1,
        choices=[
            ("C", "Create"),
            ("M", "Modify"),
            ("D", "Delete")])
    subject = models.CharField("Subject", max_length=256)
    body = models.TextField("Body")

    EXCLUDE = set([
        "admin.logentry",
        "main.audittrail",
        "kb.kbentryhistory",
        "kb/kbentrypreviewlog",
        "sa.maptask",
        "sa.reducetask",
    ])

    @classmethod
    def log(cls, sender, instance, operation, message):
        """
        Log into audit trail
        """
        user = get_user()  # Retrieve user from thread local storage
        if not user or not user.is_authenticated():
            return  # No user initialized, no audit trail
        subject = unicode(instance)
        if len(subject) > 127:
            # Narrow subject
            subject = subject[:62] + " .. " + subject[-62:]
        AuditTrail(
            user=user,
            model=sender.__name__,
            db_table=sender._meta.db_table,
            operation=operation,
            subject=subject,
            body=message
        ).save()

    @classmethod
    def on_update_model(cls, sender, instance, **kwargs):
        """
        Audit trail for INSERT and UPDATE operations
        """
        #
        logger.debug("Logging change for %s", instance)
        if instance.pk:
            # Update
            try:
                old = sender.objects.get(pk=instance.pk)
            except sender.DoesNotExist:
                # Protection for correct test fixtures loading
                return
            message = []
            operation = "M"
            for f in sender._meta.fields:
                od = f.value_to_string(old)
                nd = f.value_to_string(instance)
                if f.name == "id":
                    message += ["id: %s" % nd]
                elif nd != od:
                    message += ["%s: '%s' -> '%s'" % (f.name, od, nd)]
            message = "\n".join(message)
        else:
            # New record
            operation = "C"
            message = "\n".join(["%s = %s" % (f.name, f.value_to_string(instance))
                                 for f in sender._meta.fields])
        cls.log(sender, instance, operation, message)

    @classmethod
    def on_delete_model(cls, sender, instance, **kwargs):
        """
        Audit trail for DELETE operation
        """
        #
        logger.debug("Logging deletion of %s", instance)
        operation = "D"
        message = "\n".join(["%s = %s" % (f.name, f.value_to_string(instance))
                             for f in sender._meta.fields])
        cls.log(sender, instance, operation, message)

    @classmethod
    def on_new_model(cls, sender, **kwargs):
        if str(sender._meta) in cls.EXCLUDE:
            return  # Ignore model
        # logger.debug("Adding audit trail for %s", sender._meta)
        django_signals.post_save.connect(cls.on_update_model,
                                         sender=sender)
        django_signals.post_delete.connect(cls.on_delete_model,
                                           sender=sender)

    @classmethod
    def install(cls):
        """
        Install signal handlers
        """
        if settings.IS_WEB:
            django_signals.class_prepared.connect(cls.on_new_model)
