# ---------------------------------------------------------------------
# KBEntry model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import difflib

# Third-party modules
from django.db import models
from django.contrib.postgres.fields import ArrayField

# NOC modules
from noc.core.model.base import NOCModel
from noc.main.models.language import Language
from noc.main.models.label import Label
from noc.services.web.apps.kb.parsers.loader import loader
from noc.core.model.decorator import on_delete_check


@Label.model
@on_delete_check(
    delete=[
        ("kb.KBUserBookmark", "kb_entry"),
        ("kb.KBEntryHistory", "kb_entry"),
        ("kb.KBEntryPreviewLog", "kb_entry"),
        ("kb.KBGlobalBookmark", "kb_entry"),
        ("kb.KBEntryAttachment", "kb_entry"),
    ]
)
class KBEntry(NOCModel):
    """
    KB Entry
    """

    class Meta(object):
        verbose_name = "KB Entry"
        verbose_name_plural = "KB Entries"
        app_label = "kb"
        db_table = "kb_kbentry"
        ordering = ("id",)

    subject = models.CharField("Subject", max_length=256)
    body = models.TextField("Body")
    language = models.ForeignKey(
        Language,
        verbose_name="Language",
        limit_choices_to={"is_active": True},
        on_delete=models.CASCADE,
    )
    markup_language = models.CharField(
        "Markup Language", max_length=16, choices=[(x, x) for x in loader]
    )
    #
    labels = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(
        models.CharField(max_length=250), blank=True, null=True, default=list
    )

    def __str__(self):
        if self.id:
            return "KB%d: %s" % (self.id, self.subject)
        else:
            return "New: %s" % self.subject

    def save(self, *args, **kwargs):
        """
        save model, compute body's diff and save event history
        """
        from noc.core.middleware.tls import get_user
        from noc.kb.models.kbentryhistory import KBEntryHistory

        user = get_user()
        if self.id:
            old_body = KBEntry.objects.get(id=self.id).body
        else:
            old_body = ""
        super().save(*args, **kwargs)
        if old_body != self.body:
            diff = "\n".join(difflib.unified_diff(self.body.splitlines(), old_body.splitlines()))
            KBEntryHistory(
                kb_entry=self,
                user=user,
                diff=diff,
                timestamp=datetime.datetime.now().replace(microsecond=0),
            ).save()

    @property
    def parser(self):
        """
        Wiki parser class
        """
        return loader[self.markup_language]

    @property
    def html(self):
        """
        Returns parsed HTML
        """
        return self.parser.to_html(self)

    @property
    def last_history(self):
        """
        Returns latest KBEntryHistory record
        """
        from .kbentryhistory import KBEntryHistory

        d = KBEntryHistory.objects.filter(kb_entry=self).order_by("-timestamp")[:1]
        if d:
            return d[0]
        return None

    @classmethod
    def last_modified(cls, num=20):
        """
        Returns a list of last modified KB Entries
        """
        from django.db import connection

        c = connection.cursor()
        c.execute(
            """
            SELECT kb_entry_id,MAX(timestamp)
            FROM kb_kbentryhistory
            GROUP BY 1
            ORDER BY 2 DESC
            LIMIT %d"""
            % num
        )
        return [KBEntry.objects.get(id=r[0]) for r in c.fetchall()]

    def log_preview(self, user):
        """
        Write article preview log
        """
        from .kbentrypreviewlog import KBEntryPreviewLog

        KBEntryPreviewLog(kb_entry=self, user=user).save()

    @property
    def preview_count(self):
        """
        Returns preview count
        """
        return self.kbentrypreviewlog_set.count()

    @classmethod
    def most_popular(cls, num=20):
        """
        Returns most popular articles
        """
        from django.db import connection

        c = connection.cursor()
        c.execute(
            """
            SELECT kb_entry_id,COUNT(*)
            FROM kb_kbentrypreviewlog
            GROUP BY 1
            ORDER BY 2 DESC
            LIMIT %d"""
            % num
        )
        return [KBEntry.objects.get(id=r[0]) for r in c.fetchall()]

    @classmethod
    def upload_to(cls, instance, filename):
        """
        Callable for KBEntryAttachment.file.upload_to
        """
        return "kb/%d/%s" % (instance.kb_entry.id, filename)

    @property
    def visible_attachments(self):
        """
        Returns a list of visible attachments
        """
        return [
            {"name": x.name, "size": x.size, "mtime": x.mtime, "description": x.description}
            for x in self.kbentryattachment_set.filter(is_hidden=False).order_by("name")
        ]

    @property
    def has_visible_attachments(self):
        return self.kbentryattachment_set.filter(is_hidden=False).exists()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_kbentry")


# No delete, fixed 'KBEntry' object has no attribute 'kbentryattachment_set'
from .kbentryattachment import KBEntryAttachment  # noqa
