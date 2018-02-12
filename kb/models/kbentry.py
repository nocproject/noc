# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# KBEntry model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import difflib
# Third-party modules
from core.model.fields import AutoCompleteTagsField
from django.db import models
# NOC modules
from noc.lib.app.site import site
from noc.main.models.language import Language
from noc.services.web.apps.kb.parsers import parser_registry


parser_registry.register_all()


class KBEntry(models.Model):
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
    language = models.ForeignKey(Language, verbose_name="Language",
                                 limit_choices_to={"is_active": True})
    markup_language = models.CharField("Markup Language", max_length="16",
                                       choices=parser_registry.choices)
    tags = AutoCompleteTagsField("Tags", null=True, blank=True)

    def __unicode__(self):
        if self.id:
            return u"KB%d: %s" % (self.id, self.subject)
        else:
            return u"New: %s" % self.subject

    def get_absolute_url(self):
        return site.reverse("kb:view:view", self.id)

    @property
    def parser(self):
        """
        Wiki parser class
        """
        return parser_registry[self.markup_language]

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
        return self.kbentryhistory_set.order_by("-timestamp")[0]

    @classmethod
    def last_modified(self, num=20):
        """
        Returns a list of last modified KB Entries
        """
        from django.db import connection

        c = connection.cursor()
        c.execute("""
            SELECT kb_entry_id,MAX(timestamp)
            FROM kb_kbentryhistory
            GROUP BY 1
            ORDER BY 2 DESC
            LIMIT %d""" % num)
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
    def most_popular(self, num=20):
        """
        Returns most popular articles
        """
        from django.db import connection

        c = connection.cursor()
        c.execute("""
            SELECT kb_entry_id,COUNT(*)
            FROM kb_kbentrypreviewlog
            GROUP BY 1
            ORDER BY 2 DESC
            LIMIT %d""" % num)
        return [KBEntry.objects.get(id=r[0]) for r in c.fetchall()]

    @classmethod
    def upload_to(cls, instance, filename):
        """
        Callable for KBEntryAttachment.file.upload_to
        """
        return "/kb/%d/%s" % (instance.kb_entry.id, filename)

    @property
    def visible_attachments(self):
        """
        Returns a list of visible attachments
        """
        return [{"name": x.name, "size": x.size, "mtime": x.mtime,
                 "description": x.description}
                for x in
                self.kbentryattachment_set.filter(
                    is_hidden=False).order_by("name")]

    @property
    def has_visible_attachments(self):
        return self.kbentryattachment_set.filter(is_hidden=False).exists()

    def save(self, user=None, timestamp=None):
        """
        save model, compute body's diff and save event history
        """
        if self.id:
            old_body = KBEntry.objects.get(id=self.id).body
        else:
            old_body = ""
        super(KBEntry, self).save()
        if old_body != self.body:
            diff = "\n".join(difflib.unified_diff(self.body.splitlines(),
                                                  old_body.splitlines()))
            KBEntryHistory(kb_entry=self, user=user, diff=diff,
                           timestamp=timestamp).save()

    def is_bookmarked(self, user=None):
        """
        Check has KBEntry any bookmarks
        """
        from .kbuserbookmark import KBUserBookmark
        from .kbglobalbookmark import KBGlobalBookmark
        # Check Global bookmarks
        if KBGlobalBookmark.objects.filter(kb_entry=self).count() > 0:
            return True
        return (user and
                KBUserBookmark.objects.filter(kb_entry=self,
                                              user=user).exists())

    def set_user_bookmark(self, user):
        """
        Set user bookmark
        """
        from .kbuserbookmark import KBUserBookmark
        if not KBUserBookmark.objects.filter(kb_entry=self,
                                             user=user).exists():
            KBUserBookmark(kb_entry=self, user=user).save()

    def unset_user_bookmark(self, user):
        """
        Uset user bookmark
        """
        from .kbuserbookmark import KBUserBookmark
        for b in KBUserBookmark.objects.filter(kb_entry=self, user=user):
            b.delete()


# Avoid circular references
from .kbentryhistory import KBEntryHistory
