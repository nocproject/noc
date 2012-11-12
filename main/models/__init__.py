# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Database models for main module
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
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
from tagging.models import Tag
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
##
## A hash of Model.search classmethods.
## Populated by "class_prepared" signal listener
## Model.search is a generator taking parameters (user,query,limit)
## And yielding a SearchResults (ordered by relevancy)
##
search_methods = set()
search_models = set()


def on_new_model(sender, **kwargs):
    """
    Register new search handler if model has .search() classmethod
    """
    if hasattr(sender, "search"):
        search_methods.add(getattr(sender, "search"))
    if (hasattr(sender, "get_search_Q") and
        hasattr(sender, "get_search_data")):
        search_models.add(sender)

##
## Attach to the 'class_prepared' signal
## and on_new_model on every new model
##
class_prepared.connect(on_new_model)
##
## Exclude tables from audit
##
AUDIT_TRAIL_EXCLUDE = set([
    "django_admin_log",
    "django_session",
    "auth_message",
    "main_audittrail",
    "kb_kbentryhistory",
    "kb_kbentrypreviewlog",
    "fm_eventlog",
    "sa_maptask",
    "sa_reducetask",
])


def audit_trail_save(sender, instance, **kwargs):
    """
    Audit trail for INSERT and UPDATE operations
    """
    # Exclude tables
    if sender._meta.db_table in AUDIT_TRAIL_EXCLUDE:
        return
    #
    if instance.id:
        # Update
        try:
            old = sender.objects.get(id=instance.id)
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
    AuditTrail.log(sender, instance, operation, message)


def audit_trail_delete(sender, instance, **kwargs):
    """
    Audit trail for DELETE operation
    """
    # Exclude tables
    if sender._meta.db_table in AUDIT_TRAIL_EXCLUDE:
        return
    #
    operation = "D"
    message = "\n".join(["%s = %s" % (f.name, f.value_to_string(instance))
                         for f in sender._meta.fields])
    AuditTrail.log(sender, instance, operation, message)

##
## Set up audit trail handlers
##
if settings.IS_WEB:
    pre_save.connect(audit_trail_save)
    pre_delete.connect(audit_trail_delete)
##
## Initialize download registry
##
downloader_registry.register_all()


class AuditTrail(models.Model):
    """
    Audit Trail
    """
    class Meta:
        verbose_name = "Audit Trail"
        verbose_name_plural = "Audit Trail"
        ordering = ["-timestamp"]
    user = models.ForeignKey(User, verbose_name="User")
    timestamp = models.DateTimeField("Timestamp", auto_now=True)
    model = models.CharField("Model", max_length=128)
    db_table = models.CharField("Table", max_length=128)
    operation = models.CharField("Operation", max_length=1,
                                 choices=[("C", "Create"), ("M", "Modify"),
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


class CustomFieldEnumGroup(models.Model):
    """
    Enumeration groups for custom fields
    """
    class Meta:
        verbose_name = "Enum Group"
        verbose_name_plural = "Enum Groups"

    name = models.CharField("Name", max_length=128, unique=True)
    is_active = models.BooleanField("Is Active", default=True)
    description = models.TextField("Description",
        null=True, blank=True)

    def __unicode__(self):
        return self.name


class CustomFieldEnumValue(models.Model):
    """
    Enumeration groups values
    """
    class Meta:
        verbose_name = "Enum Group Value"
        verbose_name_plural = "Enum Group Values"
        unique_together = [("enum_group", "key")]

    enum_group = models.ForeignKey(CustomFieldEnumGroup,
        verbose_name="Enum Group", related_name="enumvalue_set")
    is_active = models.BooleanField("Is Active", default=True)
    key = models.CharField("Key", max_length=256)
    value = models.CharField("Value", max_length=256)

    def __unicode__(self):
        return u"%s@%s:%s" % (self.enum_group.name,
                              self.key, self.value)

class CustomField(models.Model):
    """
    Custom field description
    """
    class Meta:
        verbose_name = "Custom Field"
        verbose_name_plural = "Custom Fields"
        unique_together = [("table", "name")]

    table = models.CharField("Table", max_length=64)
    name = models.CharField("Name", max_length=64)
    is_active = models.BooleanField("Is Active", default=True)
    label = models.CharField("Label", max_length=128)
    type = models.CharField("Type", max_length=64,
                            choices=[
                                ("str", "String"),
                                ("int", "Integer"),
                                ("bool", "Boolean"),
                                ("date", "Date"),
                                ("datetime", "Date&Time")
                            ])
    description = models.TextField("Description", null=True, blank=True)
    # Applicable only for "str" type
    max_length = models.IntegerField("Max. Length", default=0)
    regexp = models.CharField("Regexp", max_length=256, null=True, blank=True)
    # Create database index on field
    is_indexed = models.BooleanField("Is Indexed", default=False)
    # Include into the applications search fields
    is_searchable = models.BooleanField("Is Searchable", default=False)
    # Create grid filter
    # Show comboboxes in search criteria
    is_filtered = models.BooleanField("Is Filtered", default=False)
    # Field is excluded from forms
    is_hidden = models.BooleanField("Is Hidden", default=False)
    # Is enumeration?
    enum_group = models.ForeignKey(CustomFieldEnumGroup,
        verbose_name="Enum Group", null=True, blank=True)

    def __unicode__(self):
        return u"%s.%s" % (self.table, self.name)

    @property
    def db_column(self):
        return "cust_%s" % self.name

    @property
    def index_name(self):
        return "%s_%s" % (self.table, self.name)

    def get_enums(self):
        """
        Return django-compatible choices or None
        :return:
        """
        if self.enum_group:
            qs = self.enum_group.enumvalue_set\
                                .filter(is_active=True)\
                                .order_by("value")
            if self.type == "int":
                return [(int(e.key), e.value) for e in qs]
            else:
                return [(e.key, e.value) for e in qs]
        else:
            return None

    def get_field(self):
        """
        Return *Field instance
        """
        name = str(self.name)
        if self.type == "str":
            l = self.max_length if self.max_length else 256
            return models.CharField(
                name=name,
                db_column=self.db_column,
                null=True, blank=True,
                max_length=l, choices=self.get_enums())
        elif self.type == "int":
            return models.IntegerField(
                name=name,
                db_column=self.db_column,
                null=True, blank=True)
        elif self.type == "bool":
            return models.BooleanField(
                name=name,
                db_column=self.db_column,
                default=False)
        elif self.type == "date":
            return models.DateField(
                name=name,
                db_column=self.db_column,
                null=True, blank=True)
        elif self.type == "datetime":
            return models.DateTimeField(
                name=name,
                db_column=self.db_column,
                null=True, blank=True)
        else:
            raise NotImplementedError

    @property
    def db_create_statement(self):
        # @todo: Use django's capabilities to generate SQL
        # field.db_type ?
        if self.type == "str":
            ms = self.max_length if self.max_length else 256
            r = "VARCHAR(%s)" % ms
        elif self.type == "int":
            r = "INTEGER"
        elif self.type == "bool":
            r = "BOOLEAN"
        elif self.type == "date":
            r = "DATE"
        elif self.type == "datetime":
            r = "TIMESTAMP"
        else:
            raise ValueError("Invalid field type '%s'" % self.type)
        return "ALTER TABLE %s ADD COLUMN \"%s\" %s NULL" % (
            self.table, self.db_column, r
        )

    @property
    def db_drop_statement(self):
        return "ALTER TABLE %s DROP COLUMN \"%s\"" % (
            self.table, self.db_column)

    def exec_commit(self, sql):
        c = connection.cursor()
        c.execute(sql)
        c.execute("COMMIT")

    def activate_field(self):
        self.exec_commit(self.db_create_statement)

    def deactivate_field(self):
        self.exec_commit(self.db_drop_statement)

    def create_index(self):
        self.exec_commit("CREATE INDEX %s ON %s(%s)" % (
            self.index_name, self.table, self.db_column))

    def drop_index(self):
        self.exec_commit("DROP INDEX %s" % self.index_name)

    def rename(self, old_name):
        self.exec_commit("ALTER TABLE %s RENAME \"%s\" TO \"%s\"" % (
            self.table, old_name, self.db_column
        ))

    def save(self, *args, **kwargs):
        """
        Create actual database field
        """
        if self.id:
            old = CustomField.objects.get(id=self.id)
            old_active = old.is_active
            old_indexed = old.is_indexed
            if old.name != self.name:
                self.rename(old.db_column)
        else:
            old_active = False
            old_indexed = False
        if not self.is_active:
            self.is_indexed = False
        super(CustomField, self).save(*args, **kwargs)
        if old_active != self.is_active:
            # Field status changed
            if self.is_active:
                self.activate_field()
                if self.is_indexed:
                    self.create_index()
            else:
                self.deactivate_field()
        elif self.is_indexed != old_indexed:
            if self.is_indexed:
                self.create_index()
            else:
                self.drop_index()

    def delete(self):
        if self.is_active:
            self.deactivate_field()
        super(CustomField, self).delete()

    def model_class(self):
        """
        Return appropriative Model class
        """
        a, m = self.table.split("_", 1)
        return models.get_model(a, m)

    @classmethod
    def table_fields(cls, table):
        return CustomField.objects.filter(is_active=True, table=table)

    @classmethod
    def install_fields(cls):
        """
        Install custom fields to models.
        Must be called after all models are initialized
        """
        m = None
        for f in cls.objects.filter(is_active=True).order_by("table"):
            # Get model
            if m is None or m._meta.db_table != f.table:
                m = f.model_class()
            # Install field
            mf = f.get_field()
            mf.contribute_to_class(m, str(f.name))

    @property
    def ext_model_field(self):
        """
        Dict containing ExtJS model field description
        """
        f = {
            "name": self.name,
            "type": {
                "str": "string",
                "int": "int",
                "bool": "boolean",
                "date": "date",
                "datetime": "date"
            }[self.type]
        }
        return f

    @property
    def ext_grid_column(self):
        """
        Dict containing ExtJS grid column description
        """
        f = {
            "text": self.label,
            "dataIndex": self.name,
            "hidden": True
        }
        if self.type == "bool":
            f["renderer"] = "NOC.render.Bool"
        return f

    @property
    def ext_form_field(self):
        """
        Dict containing ExtJS form field description
        """
        if self.type == "bool":
            f = {
                "name": self.name,
                "xtype": "checkboxfield",
                "boxLabel": self.label,
                "allowBlank": True
            }
        elif self.type == "str" and self.enum_group:
            f = {
                "name": self.name,
                "xtype": "combobox",
                "fieldLabel": self.label,
                "allowBlank": True,
                "queryMode": "local",
                "displayField": "label",
                "valueField": "id",
                "store": {
                    "fields": ["id", "label"],
                    "data": [
                        {"id": k, "label": v}
                        for k, v in self.get_enums()
                    ]
                }
            }
        elif self.type in ("str", "int", "date", "datetime"):
            f = {
                "name": self.name,
                "xtype": {
                    "str": "textfield",
                    "int": "numberfield",
                    "date": "datefield",
                    "datetime": "datefield"
                }[self.type],
                "fieldLabel": self.label,
                "allowBlank": True
            }
            if self.type == "str" and self.regexp:
                f["regex"] = self.regexp
        else:
            raise ValueError("Invalid field type '%s'" % self.type)
        return f

    def get_choices(self):
        """
        Returns django-compatible choices
        """
        c = connection.cursor()
        c.execute("""
            SELECT DISTINCT \"%(col)s\"
            FROM %(table)s
            WHERE \"%(col)s\" IS NOT NULL AND \"%(col)s\" != ''
            ORDER BY \"%(col)s\"""" % {
            "col": self.db_column,
            "table":self.table
        })
        return [(x, x) for x, in c.fetchall()]

    @classmethod
    def table_search_Q(cls, table, query):
        q = []
        for f in CustomField.objects.filter(is_active=True,
            table=table, is_searchable=True):
            if f.type == "str":
                q += [{"%s__icontains" % f.name: query}]
            elif f.type == "int":
                if is_int(query):
                    q += [{f.name: int(query)}]
        if q:
            return reduce(lambda x, y: x | models.Q(**y), q,
                models.Q(**q[0]))
        else:
            return None


class Permission(models.Model):
    """
    Permissions.

    Populated by manage.py sync-perm
    @todo: Check name format
    """
    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"

    name = models.CharField("Name", max_length=128, unique=True)  # module:app:permission
    implied = models.CharField("Implied", max_length=256, null=True, blank=True)  # comma-separated
    users = models.ManyToManyField(User, related_name="noc_user_permissions")
    groups = models.ManyToManyField(Group, related_name="noc_group_permissions")

    def __unicode__(self):
        return self.name

    def get_implied_permissions(self):
        if not self.implied:
            return []
        return [Permission.objects.get(name=p.strip())
                for p in self.implied.split(",")]

    @classmethod
    def has_perm(cls, user, perm):
        """
        Check user has permission either directly either via groups
        """
        if not user.is_active:
            return False
        if user.is_superuser:
            return True
        request = get_request()
        if request and "PERMISSIONS" in request.session:
            return perm in request.session["PERMISSIONS"]
        else:
            return perm in cls.get_effective_permissions(user)

    @classmethod
    def get_user_permissions(cls, user):
        """
        Return a set of user permissions
        """
        return set(user.noc_user_permissions.values_list("name", flat=True))

    @classmethod
    def set_user_permissions(cls, user, perms):
        """
        Set user permissions

        :param user: User
        :type user: User
        :param perms: Set of new permissions
        :type perms: Set
        """
        # Add implied permissions
        perms = set(perms)  # Copy
        for p in cls.objects.filter(name__in=list(perms), implied__isnull=False):
            perms.update([x.strip() for x in p.implied.split(",")])
        #
        current = cls.get_user_permissions(user)
        # Add new permissions
        for p in perms - current:
            try:
                Permission.objects.get(name=p).users.add(user)
            except Permission.DoesNotExist:
                raise Permission.DoesNotExist("Permission '%s' does not exist" % p)
        # Revoke permission
        for p in current - perms:
            Permission.objects.get(name=p).users.remove(user)

    @classmethod
    def get_group_permissions(cls, group):
        """
        Get set of group permissions
        """
        return set(group.noc_group_permissions.values_list("name", flat=True))

    @classmethod
    def set_group_permissions(cls, group, perms):
        """
        Set group permissions

        :param group: Group
        :type group: Group
        :param perms: Set of permissions
        :type perms: Set
        """
        # Add implied permissions
        perms = set(perms)  # Copy
        for p in cls.objects.filter(name__in=list(perms), implied__isnull=False):
            perms.update([x.strip() for x in p.implied.split(",")])
        #
        current = cls.get_group_permissions(group)
        # Add new permissions
        for p in perms - current:
            Permission.objects.get(name=p).groups.add(group)
        # Revoke permissions
        for p in current - perms:
            Permission.objects.get(name=p).groups.remove(group)

    @classmethod
    def get_effective_permissions(cls, user):
        """
        Returns a set of effective user permissions,
        counting group and implied ones
        """
        if user.is_superuser:
            return set(Permission.objects.values_list("name", flat=True))
        perms = set()
        # User permissions
        for p in user.noc_user_permissions.all():
            perms.add(p.name)
            if p.implied:
                perms.update(p.implied.split(","))
        # Group permissions
        for g in user.groups.all():
            for p in g.noc_group_permissions.all():
                perms.add(p.name)
                if p.implied:
                    perms.update(p.implied.split(","))
        return perms


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
        return "%s: %s" % (self.user_id, name)

from style import Style


class Language(models.Model):
    """
    Language
    """
    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"
        ordering = ["name"]

    name = models.CharField("Name", max_length=32, unique=True)
    native_name = models.CharField("Native Name", max_length=32)
    is_active = models.BooleanField("Is Active", default=False)

    def __unicode__(self):
        return self.name


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
            m = MIMEType.objects.get(extension=ext)
            return m.mime_type
        except MIMEType.DoesNotExist:
            return "application/octet-stream"


class ResourceState(models.Model):
    class Meta:
        verbose_name = "Resource State"
        verbose_name_plural = "Resource States"
        ordering = ["name"]

    name = models.CharField("Name", max_length=32, unique=True)
    description = models.TextField(null=True, blank=True)
    # State is available for selection
    is_active = models.BooleanField(default=True)
    # Only one state may be marked as "default"
    is_default = models.BooleanField(default=False)
    # State can be assigned to new record
    is_starting = models.BooleanField(default=False)
    # Resource is allowed to be provisioned
    is_provisioned = models.BooleanField(default=True)
    # Automatically step to next state when
    # resource's allocated_till field expired
    step_to = models.ForeignKey("self", blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Reset default when necessary
        """
        if self.is_default:
            # Reset previous default
            try:
                r = ResourceState.objects.get(is_default=True)
                if r.id != self.id:
                    r.is_default = False
                    r.save()
            except ResourceState.DoesNotExist:
                pass
        super(ResourceState, self).save(*args, **kwargs)

    @classmethod
    def get_default(cls):
        return cls.objects.get(is_default=True)


class NoPyRuleException(Exception):
    pass

rx_coding = re.compile(r"^#\s*-\*-\s*coding:\s*\S+\s*-\*-\s*$", re.MULTILINE)


class PyRule(models.Model):
    class Meta:
        verbose_name = "pyRule"
        verbose_name_plural = "pyRules"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    interface = models.CharField("Interface", max_length=64,
            choices=[(i, i) for i in sorted(interface_registry)])
    description = models.TextField("Description")
    text = models.TextField("Text")
    is_builtin = models.BooleanField("Is Builtin", default=False)
    changed = models.DateTimeField("Changed", auto_now=True, auto_now_add=True)
    # Compiled pyRules cache
    compiled_pyrules = {}
    compiled_changed = {}
    compiled_lock = threading.Lock()
    NoPyRule = NoPyRuleException

    alters_data = True   # Tell Django's template engine to not call PyRule

    # Use special filter for interface
    interface.existing_choices_filter = True

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        """
        Check syntax and save
        """
        self.compile_text(unicode(self.text))
        super(PyRule, self).save(**kwargs)

    @property
    def interface_class(self):
        """
        Get interface class
        """
        return interface_registry[self.interface]

    @classmethod
    def compile_text(self, text):
        """
        Compile pyRule
        """
        # Built-in pyRule decorator
        def pyrule(f):
            f.is_pyrule = True
            return f

        # Inject @pyrule decorator into namespace
        d = {"pyrule": pyrule}
        # Remove coding declarations and \r
        text = rx_coding.sub("", text.replace("\r\n", "\n"))
        # Compile text
        exec text in d
        # Find marked pyrule
        rules = [r for r in d.values()
                 if hasattr(r, "is_pyrule") and r.is_pyrule]
        if len(rules) < 1:
            raise SyntaxError("No @pyrule decorated symbol found")
        if len(rules) != 1:
            raise SyntaxError("More than one @pyrule deorated symbols found")
        rule = rules[0]
        if not callable(rule):
            raise SyntaxError("Rule is not callable")
        return rule

    @classmethod
    def lookup(cls, name):
        if name.startswith("noc_"):
            l = [name]
        else:
            l = [name, "noc_%s" % name]
        for n in l:
            try:
                return cls.objects.get(name=n)
            except cls.DoesNotExist:
                pass
        raise cls.NoPyRule

    ##
    ## Call pyRule
    ##
    def __call__(self, **kwargs):
        t = datetime.datetime.now()
        # Try to get compiled rule from cache
        with self.compiled_lock:
            requires_recompile = (self.name not in self.compiled_changed or
                                  self.compiled_changed[self.name] < self.changed)
            if not requires_recompile:
                f = self.compiled_pyrules[self.name]
        # Recompile rule and place in cache when necessary
        if requires_recompile:
            f = self.compile_text(str(self.text))
            with self.compiled_lock:
                self.compiled_pyrules[self.name] = f
                self.compiled_changed[self.name] = t
        # Check interface
        i = self.interface_class()
        kwargs = i.clean(**kwargs)
        # Evaluate pyRule
        result = f(**kwargs)
        # Check and result
        return i.clean_result(result)

    @classmethod
    def call(cls, py_rule_name, **kwargs):
        """
        Call pyRule by name
        """
        return cls.lookup(py_rule_name)(**kwargs)

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

    @classmethod
    def search(cls, user, search, limit):
        """
        Search engine plugin
        """
        from noc.lib.search import SearchResult  # Must be inside method to prevent import loops

        for b in RefBook.objects.filter(is_enabled=True):
            field_names = [f.name for f in b.refbookfield_set.order_by("order")]
            for f in b.refbookfield_set.filter(search_method__isnull=False):
                x = f.get_extra(search)
                if not x:
                    continue
                q = RefBookData.objects.filter(ref_book=b).extra(**x)
                for r in q:
                    text = "\n".join(["%s = %s" % (k, v)
                                      for k, v in zip(field_names, r.value)])
                    yield SearchResult(
                        url=("main:refbook:item", b.id, r.id),
                        title=u"Reference Book: %s, column %s" % (b.name, f.name),
                        text=text,
                        relevancy=1.0,
                    )

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


class TimePattern(models.Model):
    """
    Time Patterns
    """
    class Meta:
        verbose_name = "Time Pattern"
        verbose_name_plural = "Time Patterns"

    name = models.CharField("Name", max_length=64, unique=True)
    description = models.TextField("Description", null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def time_pattern(self):
        """
        Returns associated Time Pattern object
        """
        return TP([t.term for t in self.timepatternterm_set.all()])

    def match(self, d):
        """
        Matches DateTime objects against time pattern
        """
        return self.time_pattern.match(d)


class TimePatternTerm(models.Model):
    """
    Time pattern terms
    """
    class Meta:
        verbose_name = "Time Pattern Term"
        verbose_name_plural = "Time Pattern Terms"
        unique_together = [("time_pattern", "term")]

    time_pattern = models.ForeignKey(TimePattern, verbose_name="Time Pattern")
    term = models.CharField("Term", max_length=256)

    def __unicode__(self):
        return u"%s: %s" % (self.time_pattern.name, self.term)

    @classmethod
    def check_syntax(cls, term):
        """
        Checks Time Pattern syntax. Raises SyntaxError in case of error
        """
        TP(term)

    def save(self, *args):
        """
        Check syntax before save
        """
        TimePatternTerm.check_syntax(self.term)
        super(TimePatternTerm, self).save(*args)


class NotificationGroup(models.Model):
    """
    Notification Groups
    """
    class Meta:
        verbose_name = "Notification Group"
        verbose_name_plural = "Notification Groups"
        ordering = [("name")]
    name = models.CharField("Name", max_length=64, unique=True)
    description = models.TextField("Description", null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def members(self):
        """
        List of (time pattern, method, params, language)
        """
        default_language = settings.LANGUAGE_CODE
        m = []
        # Collect user notifications
        for ngu in self.notificationgroupuser_set.filter(user__is_active=True):
            lang = default_language
            try:
                profile = ngu.user.get_profile()
                if profile.preferred_language:
                    lang = profile.preferred_language
            except:
                continue
            for tp, method, params in profile.contacts:
                m += [(TimePatternList([ngu.time_pattern, tp]),
                       method, params, lang)]
        # Collect other notifications
        for ngo in self.notificationgroupother_set.all():
            if ngo.notification_method == "mail" and "," in ngo.params:
                for y in ngo.params.split(","):
                    m += [(ngo.time_pattern, ngo.notification_method,
                           y.strip(), default_language)]
            else:
                m += [(ngo.time_pattern, ngo.notification_method,
                       ngo.params, default_language)]
        return m

    @property
    def active_members(self):
        """
        List of currently active members: (method, param, language)
        """
        now = datetime.datetime.now()
        return set([(method, param, lang) for tp, method, param, lang
            in self.members if tp.match(now)])

    @property
    def languages(self):
        """
        List of preferred languages for users
        """
        return set([x[3] for x in self.members])

    @classmethod
    def get_effective_message(cls, messages, lang):
        for cl in (lang, settings.LANGUAGE_CODE, "en"):
            if cl in messages:
                return messages[cl]
        return "Cannot translate message"

    def notify(self, subject, body, link=None):
        """
        Send message to active members
        """
        if type(subject) != types.DictType:
            subject = {settings.LANGUAGE_CODE: subject}
        if type(body) != types.DictType:
            body = {settings.LANGUAGE_CODE: body}
        for method, params, lang in self.active_members:
            Notification(
                notification_method=method,
                notification_params=params,
                subject=self.get_effective_message(subject, lang),
                body=self.get_effective_message(body, lang),
                link=link
            ).save()

    @classmethod
    def group_notify(cls, groups, subject, body, link=None):
        """
        Send notification to a list of groups
        Prevent duplicated messages
        """
        if type(subject) != types.DictType:
            subject = {settings.LANGUAGE_CODE: subject}
        if type(body) != types.DictType:
            body = {settings.LANGUAGE_CODE: body}
        ngs = set()
        lang = {}  # (method, params) -> lang
        for g in groups:
            for method, params, l in g.active_members:
                ngs.add((method, params))
                lang[(method, params)] = l
        for method, params in ngs:
            l = lang[(method, params)]
            Notification(
                notification_method=method,
                notification_params=params,
                subject=cls.get_effective_message(subject, l),
                body=cls.get_effective_message(body, l),
                link=link
            ).save()


##
## Users in Notification Groups
##
class NotificationGroupUser(models.Model):
    class Meta:
        verbose_name = "Notification Group User"
        verbose_name_plural = "Notification Group Users"
        unique_together = [("notification_group", "time_pattern", "user")]

    notification_group = models.ForeignKey(NotificationGroup,
                                           verbose_name="Notification Group")
    time_pattern = models.ForeignKey(TimePattern, verbose_name="Time Pattern")
    user = models.ForeignKey(User, verbose_name="User")

    def __unicode__(self):
        return u"%s: %s: %s" % (self.notification_group.name,
                                self.time_pattern.name, self.user.username)

##
## Other Notification Group Items
##
NOTIFICATION_METHOD_CHOICES = [("mail", "Email"), ("file", "File")]
USER_NOTIFICATION_METHOD_CHOICES = [("mail", "Email")]


class NotificationGroupOther(models.Model):
    class Meta:
        verbose_name = "Notification Group Other"
        verbose_name_plural = "Notification Group Others"
        unique_together = [("notification_group", "time_pattern",
                            "notification_method", "params")]

    notification_group = models.ForeignKey(NotificationGroup,
                                           verbose_name="Notification Group")
    time_pattern = models.ForeignKey(TimePattern, verbose_name="Time Pattern")
    notification_method = models.CharField("Method", max_length=16,
                                           choices=NOTIFICATION_METHOD_CHOICES)
    params = models.CharField("Params", max_length=256)

    def __unicode__(self):
        return u"%s: %s: %s: %s" % (self.notification_group.name,
                                    self.time_pattern.name,
                                    self.notification_method, self.params)


class Notification(models.Model):
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    timestamp = models.DateTimeField("Timestamp", auto_now=True,
                                     auto_now_add=True)
    notification_method = models.CharField("Method", max_length=16,
                                           choices=NOTIFICATION_METHOD_CHOICES)
    notification_params = models.CharField("Params", max_length=256)
    subject = models.CharField("Subject", max_length=256)
    body = models.TextField("Body")
    link = models.CharField("Link", max_length=256, null=True, blank=True)
    next_try = models.DateTimeField("Next Try", null=True, blank=True)
    actual_till = models.DateTimeField("Actual Till", null=True, blank=True)

    def __unicode__(self):
        return self.subject


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


class UserProfileManager(models.Manager):
    """
    @todo: remove
    User Profile Manager
    Leave only current user's profile
    """
    def get_query_set(self):
        user = get_user()
        if user:
            # Create profile when necessary
            try:
                p = super(UserProfileManager, self).get_query_set().get(user=user)
            except UserProfile.DoesNotExist:
                UserProfile(user=user).save()
            return super(UserProfileManager, self).get_query_set().filter(user=user)
        else:
            return super(UserProfileManager, self).get_query_set()


class UserProfile(models.Model):
    """
    User profile
    """
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    user = models.ForeignKey(User, unique=True)
    # User data
    preferred_language = models.CharField("Preferred Language", max_length=16,
                                          null=True, blank=True,
                                          default=settings.LANGUAGE_CODE,
                                          choices=settings.LANGUAGES)
    theme = models.CharField("Theme", max_length=32, null=True, blank=True)
    #
    objects = UserProfileManager()

    def __unicode__(self):
        return "%s's Profile" % self.user.username

    def save(self, **kwargs):
        user = get_user()
        if user and self.user != user:
            raise Exception("Invalid user")
        super(UserProfile, self).save(**kwargs)

    @property
    def contacts(self):
        return [(c.time_pattern, c.notification_method, c.params)
            for c in self.userprofilecontact_set.all()]

    @property
    def active_contacts(self):
        """
        Get list of currently active contacts

        :returns: List of (method, params)
        """
        now = datetime.datetime.now()
        return [(c.notification_method, c.params)
            for c in self.contacts if c.time_pattern.match(now)]


class UserProfileContact(models.Model):
    class Meta:
        verbose_name = "User Profile Contact"
        verbose_name_plural = "User Profile Contacts"
        unique_together = [("user_profile", "time_pattern",
                            "notification_method", "params")]
    user_profile = models.ForeignKey(UserProfile, verbose_name="User Profile")
    time_pattern = models.ForeignKey(TimePattern, verbose_name="Time Pattern")
    notification_method = models.CharField("Method", max_length=16,
                                    choices=USER_NOTIFICATION_METHOD_CHOICES)
    params = models.CharField("Params", max_length=256)


##
## Triggers
##
def model_choices():
    for m in models.get_models():
        yield (m._meta.db_table, m._meta.db_table)


class DBTrigger(models.Model):
    class Meta:
        verbose_name = "Database Trigger"
        verbose_name_plural = "Database Triggers"
        ordering = ("model", "order")

    name = models.CharField("Name", max_length=64, unique=True)
    model = models.CharField("Model", max_length=128, choices=model_choices())
    is_active = models.BooleanField("Is Active", default=True)
    order = models.IntegerField("Order", default=100)
    description = models.TextField("Description", null=True, blank=True)
    pre_save_rule = models.ForeignKey(PyRule,
            verbose_name="Pre-Save Rule",
            related_name="dbtrigger_presave_set",
            limit_choices_to={"interface": "IDBPreSave"},
            blank=True, null=True)
    post_save_rule = models.ForeignKey(PyRule,
            verbose_name="Post-Save Rule",
            related_name="dbtrigger_postsave_set",
            limit_choices_to={"interface": "IDBPostSave"},
            blank=True, null=True)
    pre_delete_rule = models.ForeignKey(PyRule,
            verbose_name="Pre-Delete Rule",
            related_name="dbtrigger_predelete_set",
            limit_choices_to={"interface": "IDBPreDelete"},
            blank=True, null=True)
    post_delete_rule = models.ForeignKey(PyRule,
            verbose_name="Post-Delete Rule",
            related_name="dbtrigger_postdelete_set",
            limit_choices_to={"interface": "IDBPostDelete"},
            blank=True, null=True)
    ## State cache
    _pre_save_triggers = {}     # model.meta.db_table -> [rules]
    _post_save_triggers = {}    # model.meta.db_table -> [rules]
    _pre_delete_triggers = {}   # model.meta.db_table -> [rules]
    _post_delete_triggers = {}  # model.meta.db_table -> [rules]

    def __unicode__(self):
        return u"%s: %s" % (self.model, self.name)

    ##
    ## Refresh triggers cache
    ##
    @classmethod
    def refresh_cache(cls, *args, **kwargs):
        # Clear cache
        cls._pre_save_triggers = {}
        cls._post_save_triggers = {}
        cls._pre_delete_triggers = {}
        cls._post_delete_triggers = {}
        # Add all active triggers
        for t in cls.objects.filter(is_active=True).order_by("order"):
            for r in ["pre_save", "post_save", "pre_delete", "post_delete"]:
                c = getattr(cls, "_%s_triggers" % r)
                rule = getattr(t, "%s_rule" % r)
                if rule:
                    try:
                        c[t.model] += [rule]
                    except KeyError:
                        c[t.model] = [rule]

    ##
    ## Dispatcher for pre-save
    ##
    @classmethod
    def pre_save_dispatch(cls, **kwargs):
        m = kwargs["sender"]._meta.db_table
        if m in cls._pre_save_triggers:
            for t in cls._pre_save_triggers[m]:
                t(model=kwargs["sender"], instance=kwargs["instance"])

    ##
    ## Dispatcher for post-save
    ##
    @classmethod
    def post_save_dispatch(cls, **kwargs):
        m = kwargs["sender"]._meta.db_table
        if m in cls._post_save_triggers:
            for t in cls._post_save_triggers[m]:
                t(model=kwargs["sender"], instance=kwargs["instance"],
                  created=kwargs["created"])

    ##
    ## Dispatcher for pre-delete
    ##
    @classmethod
    def pre_delete_dispatch(cls, **kwargs):
        m = kwargs["sender"]._meta.db_table
        if m in cls._pre_delete_triggers:
            for t in cls._pre_delete_triggers[m]:
                t(model=kwargs["sender"], instance=kwargs["instance"])

    ##
    ## Dispatcher for post-delete
    ##
    @classmethod
    def post_delete_dispatch(cls, **kwargs):
        m = kwargs["sender"]._meta.db_table
        if m in cls._post_delete_triggers:
            for t in cls._post_delete_triggers[m]:
                t(model=kwargs["sender"], instance=kwargs["instance"])

    ##
    ## Called when all models are initialized
    ##
    @classmethod
    def x(cls):
        f = cls._meta.get_field_by_name("model")[0]
        f.choices = [(m._meta.db_table, m._meta.db_table)
            for m in models.get_models()]


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
        verbose_name = _("Checkpoing")
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


def search_tags(user, query, limit):
    """
    Search by tags
    """
    from noc.lib.search import SearchResult  # Must be inside method to prevent import loops

    # Find tags
    tags = []
    for p in query.split(","):
        p = p.strip()
        try:
            tags += [Tag.objects.get(name=p)]
        except Tag.DoesNotExist:
            return []
    if not tags:
        return []
    # Intersect tags
    r = None
    for t in tags:
        o = [o.object for o in t.items.all()]
        if r is None:
            r = set(o)
        else:
            r &= set(o)
    if not r:
        return []
    rr = []
    for i in r:
        if hasattr(i, "get_absolute_url"):
            rr += [SearchResult(
                    url=i.get_absolute_url(),
                    title=unicode(i),
                    text=i.tags,
                    relevancy=1.0,
                )]
    return rr

search_methods.add(search_tags)
