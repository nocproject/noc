# ---------------------------------------------------------------------
# Crashinfo
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import logging
import uuid

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import UUIDField, DateTimeField, StringField
import mongoengine.signals
import dateutil.parser
import orjson

# NOC modules
from noc.support.cp import CPClient
from noc.core.comp import smart_text

logger = logging.getLogger(__name__)


class Crashinfo(Document):
    meta = {
        "collection": "noc.crashinfo",
        "strict": False,
        "auto_create_index": False,
        "indexes": [("status", "timestamp")],
    }
    uuid = UUIDField(primary_key=True)
    timestamp = DateTimeField(required=True)
    status = StringField(
        choices=[
            ("N", "New"),
            ("r", "Reporting"),
            ("R", "Reported"),
            ("X", "Rejected"),
            ("f", "Fix ready"),
            ("F", "Fixed"),
        ],
        default="N",
    )
    process = StringField()
    branch = StringField()
    tip = StringField()
    comment = StringField()
    priority = StringField(
        choices=[("I", "Info"), ("L", "Low"), ("M", "Medium"), ("H", "High"), ("C", "Critical")],
        default="I",
    )
    # @todo: comment

    NEW_ROOT = "local/cp/crashinfo/new"

    def __str__(self):
        return smart_text(self.uuid)

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
                    ci = orjson.loads(f.read())
            except Exception as why:
                logger.error("Unable to load and decode crashinfo %s: %s", u, why)
                continue
            c = Crashinfo(
                uuid=u,
                timestamp=dateutil.parser.parse(ci["ts"]),
                process=ci["process"],
                branch=ci.get("branch"),
                tip=ci.get("tip"),
                status="N",
            )
            c.save()

    @property
    def json_path(self):
        return os.path.join(self.NEW_ROOT, "%s.json" % self.uuid)

    @property
    def json(self):
        path = self.json_path
        if os.path.exists(path):
            try:
                with open(path) as f:
                    return orjson.loads(f.read())
            except Exception as why:
                logger.error("Unable to load and decode crashinfo %s: %s", self.uuid, why)
        return None

    @property
    def traceback(self):
        json = self.json
        if json:
            return json.get("traceback")
        return None

    @classmethod
    def on_delete(cls, sender, document, **kwargs):
        path = document.json_path
        if os.path.exists(path):
            logger.debug("Removing file %s", path)
            try:
                os.unlink(path)
            except OSError as why:
                logger.error("Cannot remove file %s: %s", path, why)

    def report(self):
        logger.info("Reporting crashinfo %s", self.uuid)
        if self.status not in ("N", "r"):
            raise CPClient.Error("Cannot share not-new crashinfo")
        cp = CPClient()
        if not cp.has_system():
            raise CPClient.Error("System is not registred")
        ci = self.json
        ci["comment"] = self.comment
        ci["priority"] = self.priority
        cp.report_crashinfo(ci)
        self.status = "R"
        self.save()


mongoengine.signals.pre_delete.connect(Crashinfo.on_delete, sender=Crashinfo)
