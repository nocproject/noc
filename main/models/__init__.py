# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Database models for main module
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python Modules
from __future__ import with_statement
import os
import datetime
import re
import threading
import types
## Django Modules
from django.utils.translation import ugettext_lazy as _
from django.db import models, connection
from django.contrib.auth.models import User, Group
from django.core.validators import MaxLengthValidator
from django.db.models.signals import class_prepared, pre_save, pre_delete,\
                                     post_save, post_delete
from django.template import Template as DjangoTemplate
from django.template import Context
## Third-party modules
from mongoengine.django.sessions import MongoSession
## NOC Modules
from noc import settings
from noc.lib.fields import BinaryField
from noc.lib.database_storage import DatabaseStorage as DBS
from noc.main.refbooks.downloaders import downloader_registry
from noc.lib.fields import TextArrayField, CIDRField
from noc.lib.middleware import get_user, get_request
from noc.lib.timepattern import TimePattern as TP
from noc.lib.timepattern import TimePatternList
from noc.sa.interfaces.base import interface_registry
from noc.lib.periodic import periodic_registry
from noc.lib.app.site import site
from noc.lib.validators import check_extension, check_mimetype
from noc.lib import nosql
from noc.lib.validators import is_int
## Register periodics
periodic_registry.register_all()
from audittrail import AuditTrail
AuditTrail.install()

##
## Initialize download registry
##
downloader_registry.register_all()


from customfieldenumgroup import CustomFieldEnumGroup
from customfieldenumvalue import CustomFieldEnumValue
from customfield import CustomField
from permission import Permission


class UserSession(nosql.Document):
    meta = {
        "collection": "noc.user_sessions",
        "allow_inheritance": False
    }
    session_key = nosql.StringField(primary_key=True)
    user_id = nosql.IntField()

    @classmethod
    def register(cls, session_key, user):
        UserSession(session_key=session_key,
                    user_id=user.id).save(force_insert=True)

    @classmethod
    def unregister(cls, session_key):
        UserSession.objects.filter(session_key=session_key).delete()

    @classmethod
    def active_sessions(cls, user=None, group=None):
        """
        Calculate current active sessions for user and group
        """
        ids = []
        if user:
            ids += [user.id]
        if group:
            ids += group.user_set.values_list("id", flat=True)
        n = 0
        now = datetime.datetime.now()
        for us in UserSession.objects.filter(user_id__in=ids):
            s = MongoSession.objects.filter(session_key=us.session_key).first()
            if s:
                # Session exists
                if s.expire_date < now:
                    # Expired session
                    s.delete()
                else:
                    n += 1  # Count as active
            else:
                # Hanging session, schedule to kill
                us.delete()
        return n


class UserState(nosql.Document):
    meta = {
        "collection": "noc.userstate",
        "allow_inheritance": False
    }
    user_id = nosql.IntField()
    key = nosql.StringField()
    value = nosql.StringField()

    def __unicode__(self):
        return "%s: %s" % (self.user_id, self.key)

from style import Style
from language import Language


class DatabaseStorage(models.Model):
    """
    Database Storage
    """
    class Meta:
        verbose_name = "Database Storage"
        verbose_name_plural = "Database Storage"

    name = models.CharField("Name", max_length=256, unique=True)
    data = BinaryField("Data")
    size = models.IntegerField("Size")
    mtime = models.DateTimeField("MTime")

    ##
    ## Options for DatabaseStorage
    ##
    @classmethod
    def dbs_options(cls):
        return {
            "db_table": DatabaseStorage._meta.db_table,
            "name_field": "name",
            "data_field": "data",
            "mtime_field": "mtime",
            "size_field": "size",
        }

    @classmethod
    def get_dbs(cls):
        """
        Get DatabaseStorage instance
        """
        return DBS(cls.dbs_options())
##
## Default database storage
##
database_storage = DatabaseStorage.get_dbs()


class MIMEType(models.Model):
    """
    MIME Type mapping
    """
    class Meta:
        verbose_name = "MIME Type"
        verbose_name_plural = "MIME Types"
        ordering = ["extension"]

    extension = models.CharField("Extension", max_length=32, unique=True,
                                 validators=[check_extension])
    mime_type = models.CharField("MIME Type", max_length=63,
                                 validators=[check_mimetype])

    def __unicode__(self):
        return u"%s -> %s" % (self.extension, self.mime_type)

    @classmethod
    def get_mime_type(cls, filename):
        """
        Determine MIME type from filename
        """
        r, ext = os.path.splitext(filename)
        try:
            m = MIMEType.objects.get(extension=ext.lower())
            return m.mime_type
        except MIMEType.DoesNotExist:
            return "application/octet-stream"

from resourcestate import ResourceState
from pyrule import PyRule, NoPyRuleException


##
## Search patters
##
rx_mac_3_octets = re.compile("^([0-9A-F]{6}|[0-9A-F]{12})$", re.IGNORECASE)


class RefBook(models.Model):
    """
    Reference Books
    """
    class Meta:
        verbose_name = "Ref Book"
        verbose_name_plural = "Ref Books"

    name = models.CharField("Name", max_length=128, unique=True)
    language = models.ForeignKey(Language, verbose_name="Language")
    description = models.TextField("Description", blank=True, null=True)
    is_enabled = models.BooleanField("Is Enabled", default=False)
    is_builtin = models.BooleanField("Is Builtin", default=False)
    downloader = models.CharField("Downloader", max_length=64,
            choices=downloader_registry.choices, blank=True, null=True)
    download_url = models.CharField("Download URL",
            max_length=256, null=True, blank=True)
    last_updated = models.DateTimeField("Last Updated", blank=True, null=True)
    next_update = models.DateTimeField("Next Update", blank=True, null=True)
    refresh_interval = models.IntegerField("Refresh Interval (days)", default=0)

    def __unicode__(self):
        return self.name

    def add_record(self, data):
        """
        Add new record
        :param data: Hash of field name -> value
        :type data: Dict
        """
        fields = {}
        for f in self.refbookfield_set.all():
            fields[f.name] = f.order - 1
        r = [None for f in range(len(fields))]
        for k, v in data.items():
            r[fields[k]] = v
        RefBookData(ref_book=self, value=r).save()

    def flush_refbook(self):
        """
        Delete all records in ref. book
        """
        RefBookData.objects.filter(ref_book=self).delete()

    def bulk_upload(self, data):
        """
        Bulk upload data to ref. book

        :param data: List of hashes field name -> value
        :type data: List
        """
        fields = {}
        for f in self.refbookfield_set.all():
            fields[f.name] = f.order - 1
        # Prepare empty row template
        row_template = [None for f in range(len(fields))]
        # Insert data
        for r in data:
            row = row_template[:]  # Clone template row
            for k, v in r.items():
                if k in fields:
                    row[fields[k]] = v
            RefBookData(ref_book=self, value=row).save()

    def download(self):
        """
        Download refbook
        """
        if self.downloader and self.downloader in downloader_registry.classes:
            downloader = downloader_registry[self.downloader]
            data = downloader.download(self)
            if data:
                self.flush_refbook()
                self.bulk_upload(data)
                self.last_updated = datetime.datetime.now()
                self.next_update = self.last_updated + datetime.timedelta(days=self.refresh_interval)
                self.save()

    @property
    def can_search(self):
        """
        Check refbook has at least one searchable field
        """
        return self.refbookfield_set.filter(search_method__isnull=False).exists()

    @property
    def fields(self):
        """
        Get fields names sorted by order
        """
        return self.refbookfield_set.order_by("order")


class RefBookField(models.Model):
    """
    Refbook fields
    """
    class Meta:
        verbose_name = "Ref Book Field"
        verbose_name_plural = "Ref Book Fields"
        unique_together = [("ref_book", "order"), ("ref_book", "name")]
        ordering = ["ref_book", "order"]

    ref_book = models.ForeignKey(RefBook, verbose_name="Ref Book")
    name = models.CharField("Name", max_length="64")
    order = models.IntegerField("Order")
    is_required = models.BooleanField("Is Required", default=True)
    description = models.TextField("Description", blank=True, null=True)
    search_method = models.CharField("Search Method", max_length=64,
            blank=True, null=True,
            choices=[
                ("string", "string"),
                ("substring", "substring"),
                ("starting", "starting"),
                ("mac_3_octets_upper", "3 Octets of the MAC")])

    def __unicode__(self):
        return u"%s: %s" % (self.ref_book, self.name)

    # Return **kwargs for extra
    def get_extra(self, search):
        if self.search_method:
            return getattr(self, "search_%s" % self.search_method)(search)
        else:
            return {}

    def search_string(self, search):
        """
        string search method
        """
        return {
            "where": ["value[%d] ILIKE %%s" % self.order],
            "params": [search]
        }

    def search_substring(self, search):
        """
        substring search method
        """
        return {
            "where": ["value[%d] ILIKE %%s" % self.order],
            "params": ["%" + search + "%"]
        }

    def search_starting(self, search):
        """
        starting search method
        """
        return {
            "where": ["value[%d] ILIKE %%s" % self.order],
            "params": [search + "%"]
        }

    def search_mac_3_octets_upper(self, search):
        """
        Match 3 first octets of the MAC address
        """
        mac = search.replace(":", "").replace("-", "").replace(".", "")
        if not rx_mac_3_octets.match(mac):
            return {}
        return {
            "where": ["value[%d]=%%s" % self.order],
            "params": [mac]
        }


class RBDManader(models.Manager):
    """
    Ref Book Data Manager
    """
    # Order by first field
    def get_query_set(self):
        return super(RBDManader, self).get_query_set().extra(order_by=["main_refbookdata.value[1]"])


class RefBookData(models.Model):
    """
    Ref. Book Data
    """
    class Meta:
        verbose_name = "Ref Book Data"
        verbose_name_plural = "Ref Book Data"

    ref_book = models.ForeignKey(RefBook, verbose_name="Ref Book")
    value = TextArrayField("Value")

    objects = RBDManader()

    def __unicode__(self):
        return u"%s: %s" % (self.ref_book, self.value)

    @property
    def items(self):
        """
        Returns list of pairs (field,data)
        """
        return zip(self.ref_book.fields, self.value)

from timepattern import TimePattern
from timepatternterm import TimePatternTerm


from notification import (Notification, NOTIFICATION_METHOD_CHOICES, USER_NOTIFICATION_METHOD_CHOICES)
from notificationgroup import (
    NotificationGroup, NotificationGroupUser, NotificationGroupOther,
    )

class SystemNotification(models.Model):
    """
    System Notifications
    """
    class Meta:
        verbose_name = "System Notification"
        verbose_name_plural = "System Notifications"

    name = models.CharField("Name", max_length=64, unique=True)
    notification_group = models.ForeignKey(NotificationGroup,
                                           verbose_name="Notification Group",
                                           null=True, blank=True,
                                           on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.name

    @classmethod
    def get_notification_group(cls, name):
        try:
            sn = SystemNotification.objects.get(name=name)
            return sn.notification_group
        except SystemNotification.DoesNotExist:  # Ignore undefined notifications
            return None

    @classmethod
    def notify(cls, name, subject, body, link=None):
        n = cls.get_notification_group(name)
        if n:
            n.notify(subject=subject, body=body, link=link)

from userprofile import UserProfile, UserProfileManager
from userprofilecontact import UserProfileContact
from dbtrigger import DBTrigger, model_choices



class Schedule(models.Model):
    class Meta:
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")
        ordering = ["periodic_name"]

    periodic_name = models.CharField(_("Periodic Task"), max_length=64)
    is_enabled = models.BooleanField(_("Enabled?"), default=False)
    time_pattern = models.ForeignKey(TimePattern,
                                     verbose_name=_("Time Pattern"))
    run_every = models.PositiveIntegerField(_("Run Every (secs)"),
                                     default=86400)
    timeout = models.PositiveIntegerField(_("Timeout (secs)"),
                                     null=True, blank=True)
    last_run = models.DateTimeField(_("Last Run"), blank=True, null=True)
    last_status = models.BooleanField(_("Last Status"), default=True)

    def __unicode__(self):
        return u"%s:%s" % (self.periodic_name, self.time_pattern.name)

    @property
    def periodic(self):
        return periodic_registry[self.periodic_name]

    def mark_run(self, start_time, status):
        """Set last run"""
        self.last_run = start_time
        self.last_status = status
        self.save()

    @classmethod
    def get_tasks(cls):
        """Get tasks required to run"""
        now = datetime.datetime.now()
        return [s for s in Schedule.objects.filter(is_enabled=True)
                if (s.time_pattern.match(now) and
                   (s.last_run is None or
                    s.last_run + datetime.timedelta(seconds=s.run_every) <= now))]

    @classmethod
    def reschedule(cls, name, days=0, minutes=0, seconds=0):
        """Reschedule tasks with name to launch immediately"""
        t = Schedule.objects.filter(periodic_name=name)[0]
        t.last_run = (datetime.datetime.now() -
                      datetime.timedelta(days=days, minutes=minutes,
                                         seconds=seconds))
        t.save()


class Shard(models.Model):
    class Meta:
        verbose_name = _("Shard")
        verbose_name_plural = _("Shards")
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=128, unique=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    description = models.TextField(_("Description"), null=True, blank=True)

    def __unicode__(self):
        return self.name

from prefixtable import PrefixTable, PrefixTablePrefix


class Template(models.Model):
    class Meta:
        verbose_name = _("Template")
        verbose_name_plural = _("Templates")
        ordering = ["name"]

    name = models.CharField(_("Name"), unique=True, max_length=128)
    subject = models.TextField(_("Subject"))
    body = models.TextField(_("Body"))

    def __unicode__(self):
        return self.name

    def render_subject(self, LANG=None, **kwargs):
        return DjangoTemplate(self.subject).render(Context(kwargs))

    def render_body(self, LANG=None, **kwargs):
        return DjangoTemplate(self.body).render(Context(kwargs))


class SystemTemplate(models.Model):
    class Meta:
        verbose_name = _("System template")
        verbose_name_plural = _("System templates")
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=64, unique=True)
    description = models.TextField(_("Description"), null=True, blank=True)
    template = models.ForeignKey(Template, verbose_name=_("Template"))

    def __unicode__(self):
        return self.name

    def render_subject(self, LANG=None, **kwargs):
        return self.template.render_subject(lang=LANG, **kwargs)

    def render_body(self, LANG=None, **kwargs):
        return self.template.render_body(lang=LANG, **kwargs)

    @classmethod
    def notify_users(cls, name, users, **kwargs):
        """
        Send notifications via template to users
        :param name: System template name
        :param users: List of User instances or id's
        """
        # Find system template by name
        try:
            t = cls.objects.get(name=name)
        except cls.DoesNotExist:
            return
        # Fix users
        u_list = []
        for u in users:
            if type(u) in (types.IntType, types.LongType):
                try:
                    u_list += [User.objects.get(id=u)]
                except User.DoesNotExist:
                    continue
            elif type(u) in (types.StringType, types.UnicodeType):
                u_list += [User.objects.get(username=u)]
            elif isinstance(u, User):
                u_list += [u]
        # Left only active users
        u_list = [u for u in u_list if u.is_active]
        # Send notifications


class Checkpoint(models.Model):
    """
    Checkpoint is a marked moment in time
    """
    class Meta:
        verbose_name = _("Checkpoint")
        verbose_name_plural = _("Checkpoints")

    timestamp = models.DateTimeField(_("Timestamp"))
    user = models.ForeignKey(User, verbose_name=_("User"), blank=True, null=True)
    comment = models.CharField(_("Comment"), max_length=256)
    private = models.BooleanField(_("Private"), default=False)

    def __unicode__(self):
        if self.user:
            return u"%s[%s]: %s" % (self.timestamp, self.user.username,
                                    self.comment)

    @classmethod
    def set_checkpoint(cls, comment, user=None, timestamp=None, private=True):
        if not timestamp:
            timestamp = datetime.datetime.now()
        cp = Checkpoint(timestamp=timestamp, user=user, comment=comment,
                        private=private)
        cp.save()
        return cp

from favorites import Favorites
from tag import Tag
from sync import Sync

##
## Install triggers
##
if settings.IS_WEB and not settings.IS_TEST:
    DBTrigger.refresh_cache()  # Load existing triggers
    # Trigger cache syncronization
    post_save.connect(DBTrigger.refresh_cache, sender=DBTrigger)
    post_delete.connect(DBTrigger.refresh_cache, sender=DBTrigger)
    # Install signal hooks
    pre_save.connect(DBTrigger.pre_save_dispatch)
    post_save.connect(DBTrigger.post_save_dispatch)
    pre_delete.connect(DBTrigger.pre_delete_dispatch)
    post_delete.connect(DBTrigger.post_delete_dispatch)

##
## Monkeypatch to change User.username.max_length
##
User._meta.get_field("username").max_length = User._meta.get_field("email").max_length
User._meta.get_field("username").validators = [MaxLengthValidator(User._meta.get_field("username").max_length)]
User._meta.ordering = ["username"]
