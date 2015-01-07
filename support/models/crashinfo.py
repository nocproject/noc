# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Crashinfo
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import logging
import uuid
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (UUIDField, DateTimeField, StringField)
import mongoengine.signals
import dateutil.parser
## NOC modules
from noc.lib.serialize import json_decode

logger = logging.getLogger(__name__)


class Crashinfo(Document):
    meta = {
        "collection": "noc.crashinfo",
        "indexes": [("status", "timestamp")]
    }
    uuid = UUIDField(unique=True, primary_key=True)
    timestamp = DateTimeField(required=True)
    status = StringField(
        choices=[
            ("N", "New"),
            ("r", "Reporting"),
            ("R", "Reported"),
            ("X", "Rejected"),
            ("f", "Fix ready"),
            ("F", "Fixed")
        ],
        default="N"
    )
    process = StringField()
    branch = StringField()
    tip = StringField()
    comment = StringField()
    priority = StringField(
        choices=[
            ("I", "Info"),
            ("L", "Low"),
            ("M", "Medium"),
            ("H", "High"),
            ("C", "Critical")
        ]
    )
    # @todo: comment

    NEW_ROOT = "local/cp/crashinfo/new"

    def __unicode__(self):
        return unicode(self.uuid)

    @classmethod
    def scan(cls):
        """
        Scan cls.NEW_ROOT for new crashinfos
        """
        for f in os.listdir(cls.NEW_ROOT):
            if not f.endswith(".json"):
                continue
            try:
                u = uuid.UUID(f[:-5])
            except ValueError:
                continue  # Badly formed UUID
            if Crashinfo.objects.filter(uuid=u).count():
                continue  # Known
            logger.info("New crashinfo found: %s", u)
            try:
                with open(os.path.join(cls.NEW_ROOT, f)) as f:
                    ci = json_decode(f.read())
            except Exception, why:
                logger.error(
                    "Unable to load and decode crashinfo %s: %s",
                    u, why
                )
                continue
            c = Crashinfo(
                uuid=u,
                timestamp=dateutil.parser.parse(ci["ts"]),
                process=ci["process"],
                branch=ci.get("branch"),
                tip=ci.get("tip"),
                status="N"
            )
            c.save()

    @property
    def json_path(self):
        return os.path.join(self.NEW_ROOT, "%s.json" % self.uuid)

    @property
    def traceback(self):
        path = self.json_path
        if os.path.exists(path):
            try:
                with open(path) as f:
                    ci = json_decode(f.read())
                    return ci["traceback"]
            except Exception, why:
                logger.error(
                    "Unable to load and decode crashinfo %s: %s",
                    self.uuid, why
                )
        return None

    @classmethod
    def on_delete(cls, sender, document, **kwargs):
        path = document.json_path
        if os.path.exists(path):
            logger.debug("Removing file %s", path)
            try:
                os.unlink(path)
            except OSError, why:
                logger.error("Cannot remove file %s: %s", path, why)

##
mongoengine.signals.pre_delete.connect(
    Crashinfo.on_delete,
    sender=Crashinfo
)
