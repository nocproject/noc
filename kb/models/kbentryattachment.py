# ---------------------------------------------------------------------
# KBEntryAttachment model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.main.models.databasestorage import database_storage
from noc.kb.models.kbentry import KBEntry


class KBEntryAttachment(NOCModel):
    """
    Attachments
    """

    class Meta(object):
        verbose_name = "KB Entry Attachment"
        verbose_name_plural = "KB Entry Attachments"
        app_label = "kb"
        db_table = "kb_kbentryattachment"
        unique_together = [("kb_entry", "name")]

    kb_entry = models.ForeignKey(KBEntry, verbose_name="KB Entry", on_delete=models.CASCADE)
    name = models.CharField("Name", max_length=256)
    description = models.CharField("Description", max_length=256, null=True, blank=True)
    is_hidden = models.BooleanField("Is Hidden", default=False)
    file = models.FileField("File", upload_to=KBEntry.upload_to, storage=database_storage)

    def __str__(self):
        return "%d: %s" % (self.kb_entry.id, self.name)

    def delete(self):
        """
        Delete object on database storage too
        """
        super().delete()
        self.file.storage.delete(self.file.name)

    @property
    def size(self):
        """
        File size
        """
        s = self.file.storage.stat(self.file.name)
        if s:
            return s["size"]
        return None

    @property
    def mtime(self):
        """
        File mtime
        """
        s = self.file.storage.stat(self.file.name)
        if s:
            return s["mtime"]
        return None
