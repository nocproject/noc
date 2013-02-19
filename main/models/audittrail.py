# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AuditTrail model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django models
from django.db import models
from django.contrib.auth.models import User
## NOC modules
from noc.lib.middleware import get_user


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
