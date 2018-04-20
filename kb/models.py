# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Models for KB application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import difflib
import re
## Django modules
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
## NOC modules
from noc.main.models import Language, database_storage
from noc.kb.parsers import parser_registry
from noc.lib.validators import is_int
from noc.lib.app.site import site
from noc.lib.fields import AutoCompleteTagsField

##
## Register all wiki-syntax parsers
##
parser_registry.register_all()


class KBEntry(models.Model):
    """
    KB Entry
    """
    class Meta:
        verbose_name = "KB Entry"
        verbose_name_plural = "KB Entries"
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
        if not KBUserBookmark.objects.filter(kb_entry=self,
                                             user=user).exists():
            KBUserBookmark(kb_entry=self, user=user).save()

    def unset_user_bookmark(self, user):
        """
        Uset user bookmark
        """
        for b in KBUserBookmark.objects.filter(kb_entry=self, user=user):
            b.delete()


class KBEntryAttachment(models.Model):
    """
    Attachments
    """
    class Meta:
        verbose_name = "KB Entry Attachment"
        verbose_name_plural = "KB Entry Attachments"
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


class KBEntryHistory(models.Model):
    """
    Modification History
    """
    class Meta:
        verbose_name = "KB Entry History"
        verbose_name_plural = "KB Entry Histories"
        ordering = ("kb_entry", "timestamp")

    kb_entry = models.ForeignKey(KBEntry, verbose_name="KB Entry")
    timestamp = models.DateTimeField("Timestamp", auto_now_add=True)
    user = models.ForeignKey(User, verbose_name="User")
    diff = models.TextField("Diff")


class KBEntryPreviewLog(models.Model):
    """
    Preview Log
    """
    class Meta:
        verbose_name = "KB Entry Preview Log"
        verbose_name_plural = "KB Entry Preview Log"

    kb_entry = models.ForeignKey(KBEntry, verbose_name="KB Entry")
    timestamp = models.DateTimeField("Timestamp", auto_now_add=True)
    user = models.ForeignKey(User, verbose_name="User")


class KBGlobalBookmark(models.Model):
    """
    Global Bookmarks
    """
    class Meta:
        verbose_name = "KB Global Bookmark"
        verbose_name_plural = "KB Global Bookmarks"

    kb_entry = models.ForeignKey(KBEntry, verbose_name="KBEntry", unique=True)

    def __unicode__(self):
        return unicode(self.kb_entry)


class KBUserBookmark(models.Model):
    """
    User Bookmarks
    """
    class Meta:
        verbose_name = "KB User Bookmark"
        verbose_name_plural = "KB User Bookmarks"
        unique_together = [("user", "kb_entry")]

    user = models.ForeignKey(User, verbose_name="User")
    kb_entry = models.ForeignKey(KBEntry, verbose_name="KBEntry")

    def __unicode__(self):
        return u"%s: %s" % (unicode(self.user), unicode(self.kb_entry))

## Regular expression to match template variable
rx_template_var = re.compile("{{([^}]+)}}", re.MULTILINE)


class KBEntryTemplate(models.Model):
    """
    KB Entry Template
    """
    class Meta:
        verbose_name = "KB Entry Template"
        verbose_name_plural = "KB Entry Templates"
        ordering = ("id",)

    name = models.CharField("Name", max_length=128, unique=True)
    subject = models.CharField("Subject", max_length=256)
    body = models.TextField("Body")
    language = models.ForeignKey(Language, verbose_name="Language",
                                 limit_choices_to={"is_active": True})
    markup_language = models.CharField("Markup Language", max_length="16",
                                       choices=parser_registry.choices)
    tags = AutoCompleteTagsField("Tags", null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return site.reverse("kb:kbentrytemplate:change", self.id)

    @property
    def _var_list(self):
        """
        Returns template variables list
        """
        var_set = set(rx_template_var.findall(self.subject))
        var_set.update(rx_template_var.findall(self.body))
        return sorted(var_set)
