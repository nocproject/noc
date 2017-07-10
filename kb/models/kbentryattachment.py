# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# KBEntryAttachment model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.db import models
from django.db.models import Q
# NOC modules
from noc.main.models.databasestorage import database_storage
from noc.kb.models.kbentry import KBEntry


class KBEntryAttachment(models.Model):
    """
    Attachments
    """
    class Meta:
        verbose_name = "KB Entry Attachment"
        verbose_name_plural = "KB Entry Attachments"
        app_label = "kb"
        db_table = "kb_kbentryattachment"
        unique_together = [("kb_entry", "name")]

    kb_entry = models.ForeignKey(KBEntry, verbose_name="KB Entry")
    name = models.CharField("Name", max_length=256)
    description = models.CharField("Description", max_length=256, null=True,
                                   blank=True)
    is_hidden = models.BooleanField("Is Hidden", default=False)
    file = models.FileField("File", upload_to=KBEntry.upload_to,
                            storage=database_storage)

    def __unicode__(self):
        return u"%d: %s" % (self.kb_entry.id, self.name)

    def delete(self):
        """
        Delete object on database storage too
        """
        super(KBEntryAttachment, self).delete()
        self.file.storage.delete(self.file.name)

    @property
    def size(self):
        """
        File size
        """
        s = self.file.storage.stat(self.file.name)
        if s:
            return s["size"]
        else:
            return None

    @property
    def mtime(self):
        """
        File mtime
        """
        s = self.file.storage.stat(self.file.name)
        if s:
            return s["mtime"]
        else:
            return None

    @classmethod
    def search(cls, user, query, limit):
        """
        Search engine
        """
        if user.has_perm("kb.change_kbentry"):
            q = Q(name__icontains=query) | Q(description__icontains=query)
            for r in KBEntryAttachment.objects.filter(q):
                yield SearchResult(
                    url=("kb:view:view", r.kb_entry.id),
                    title="KB%d: %s" % (r.kb_entry.id, r.kb_entry.subject),
                    text="Attachement: %s (%s)" % (r.name, r.description),
                    relevancy=1.0)
