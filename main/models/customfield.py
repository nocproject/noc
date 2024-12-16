# ---------------------------------------------------------------------
# CustomField model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
from functools import reduce
import threading

# Third-party modules
from django.db import models, connection
from django.db.models import signals as django_signals
from django.apps import apps
from mongoengine.base.common import _document_registry
from mongoengine import fields
import mongoengine.signals

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.validators import is_int
from noc.core.comp import smart_text
from .customfieldenumgroup import CustomFieldEnumGroup
from .customfieldenumvalue import CustomFieldEnumValue

logger = logging.getLogger(__name__)
id_lock = threading.Lock()


class CustomField(NOCModel):
    """
    Custom field description
    """

    class Meta(object):
        verbose_name = "Custom Field"
        verbose_name_plural = "Custom Fields"
        db_table = "main_customfield"
        app_label = "main"
        unique_together = [("table", "name")]

    table = models.CharField("Table", max_length=64)
    name = models.CharField("Name", max_length=64)
    is_active = models.BooleanField("Is Active", default=True)
    label = models.CharField("Label", max_length=128)
    type = models.CharField(
        "Type",
        max_length=64,
        choices=[
            ("str", "String"),
            ("int", "Integer"),
            ("bool", "Boolean"),
            ("date", "Date"),
            ("datetime", "Date&Time"),
        ],
    )
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
    enum_group = models.ForeignKey(
        CustomFieldEnumGroup,
        verbose_name="Enum Group",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    _cfields = {}
    _installed = set()
    _table_fields = None

    def __str__(self):
        return "%s.%s" % (self.table, self.name)

    @property
    def is_table(self):
        return "." not in self.table

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
            qs = CustomFieldEnumValue.objects.filter(
                is_active=True, enum_group=self.enum_group
            ).order_by("value")
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
        if self.is_table:
            if self.type == "str":
                max_length = self.max_length if self.max_length else 256
                return models.CharField(
                    name=name,
                    db_column=self.db_column,
                    null=True,
                    blank=True,
                    max_length=max_length,
                    choices=self.get_enums(),
                )
            elif self.type == "int":
                return models.IntegerField(
                    name=name, db_column=self.db_column, null=True, blank=True
                )
            elif self.type == "bool":
                return models.BooleanField(name=name, db_column=self.db_column, default=False)
            elif self.type == "date":
                return models.DateField(name=name, db_column=self.db_column, null=True, blank=True)
            elif self.type == "datetime":
                return models.DateTimeField(
                    name=name, db_column=self.db_column, null=True, blank=True
                )
            else:
                raise NotImplementedError
        else:
            if self.type == "str":
                return fields.StringField(db_field=self.db_column, required=False)
            elif self.type == "int":
                return fields.IntField(db_field=self.db_column, required=False)
            elif self.type == "bool":
                return fields.BooleanField(db_field=self.db_column, required=False)
            elif self.type in ("date", "datetime"):
                return fields.DateTimeField(db_field=self.db_column, required=False)
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
        return 'ALTER TABLE %s ADD COLUMN "%s" %s NULL' % (self.table, self.db_column, r)

    @property
    def db_drop_statement(self):
        return 'ALTER TABLE %s DROP COLUMN "%s"' % (self.table, self.db_column)

    def execute(self, sql):
        logger.debug("Execute: %s", sql)
        c = connection.cursor()
        c.execute(sql)

    def activate_field(self):
        logger.info("Activating field %s.%s", self.table, self.name)
        if self.is_table:
            self.execute(self.db_create_statement)

    def deactivate_field(self):
        logger.info("Deactivating field %s.%s", self.table, self.name)
        if self.is_table:
            self.execute(self.db_drop_statement)

    def create_index(self):
        logger.info("Creating index %s", self.index_name)
        if self.is_table:
            self.execute(
                "CREATE INDEX %s ON %s(%s)" % (self.index_name, self.table, self.db_column)
            )

    def drop_index(self):
        logger.info("Dropping index %s", self.index_name)
        if self.is_table:
            self.execute("DROP INDEX %s" % self.index_name)

    def rename(self, old):
        logger.info(
            "Renaming custom field %s.%s to %s.%s",
            old.table,
            old.name,
            self.table,
            self.name,
        )
        if self.is_table:
            self.execute(
                'ALTER TABLE %s RENAME "%s" TO "%s"' % (self.table, old.name, self.db_column)
            )

    def save(self, *args, **kwargs):
        """
        Create actual database field
        """
        if self.id:
            old = CustomField.objects.get(id=self.id)
            old_active = old.is_active
            old_indexed = old.is_indexed
            if old.name != self.name:
                self.rename(old)
        else:
            old_active = False
            old_indexed = False
        if not self.is_active:
            self.is_indexed = False
        super().save(*args, **kwargs)
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

    def delete(self, using=None):
        if self.is_active:
            self.deactivate_field()
        super().delete(using=using)

    def model_class(self):
        """
        Return appropriate Model class
        """
        a, m = self.table.split("_", 1)
        if a == "auth":
            a = "aaa"
        return apps.get_model(a, m)

    def document_class(self):
        """
        Return appropriate document class
        """
        for dc in _document_registry.values():
            if dc._get_collection_name() == self.table:
                return dc
        return None

    @classmethod
    def table_fields(cls, table):
        with id_lock:
            if cls._table_fields is None:
                cls._table_fields = {}
                for cf in CustomField.objects.filter(is_active=True):
                    if cf.table not in cls._table_fields:
                        cls._table_fields[cf.table] = []
                    cls._table_fields[cf.table] += [cf]
            return cls._table_fields.get(table, [])

    @classmethod
    def install_fields(cls):
        """
        Install custom fields to models.
        Must be called after all models are initialized
        """
        for f in cls.objects.filter(is_active=True).order_by("table"):
            if f.table not in cls._cfields:
                if f.is_table:
                    django_signals.class_prepared.connect(cls.on_new_model)
                else:
                    mongoengine.signals.pre_init.connect(cls.on_new_document)
                cls._cfields[f.table] = [f]
            else:
                cls._cfields[f.table] += [f]
        # Initialize already installed models
        for t in cls._cfields:
            t0 = cls._cfields[t][0]
            try:
                if t0.is_table:
                    m = t0.model_class()
                else:
                    m = t0.document_class()
            except Exception:
                m = 0
            if m:
                # Install existing fields
                for f in cls._cfields[t]:
                    f.install_field()

    def install_field(self):
        """
        Install custom field to model
        """
        un = smart_text(self)
        if un in self._installed:
            return
        self._installed.add(un)
        fn = str(self.name)
        logger.info("Installing custom field %s.%s", self.table, self.name)
        mf = self.get_field()
        if self.is_table:
            # Install model field
            m = self.model_class()
            mf.contribute_to_class(m, fn)
        else:
            # Install document field
            m = self.document_class()
            setattr(m, fn, mf)
            mf.name = fn
            m._fields[fn] = mf
            m._db_field_map[fn] = mf.db_field
            m._reverse_db_field_map[mf.db_field] = fn
            m._fields_ordered = m._fields_ordered + (fn,)

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
                "datetime": "date",
            }[self.type],
        }
        return f

    @property
    def ext_grid_column(self):
        """
        Dict containing ExtJS grid column description
        """
        f = {"text": self.label, "dataIndex": self.name, "hidden": True}
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
                "allowBlank": True,
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
                    "data": [{"id": k, "label": v} for k, v in self.get_enums()],
                },
            }
        elif self.type in ("str", "int", "date", "datetime"):
            f = {
                "name": self.name,
                "xtype": {
                    "str": "textfield",
                    "int": "numberfield",
                    "date": "datefield",
                    "datetime": "datefield",
                }[self.type],
                "fieldLabel": self.label,
                "allowBlank": True,
            }
            if self.type == "str" and self.regexp:
                f["regex"] = self.regexp
            if self.type == "date":
                f["format"] = "Y-m-d"
                f["altFormats"] = "Y-m-d"
            if self.type == "datetime":
                f["format"] = "Y-m-d H:i:s"
                f["altFormats"] = "Y-m-d\\TH:i:s"
        else:
            raise ValueError("Invalid field type '%s'" % self.type)
        return f

    def get_choices(self):
        """
        Returns django-compatible choices
        """
        c = connection.cursor()
        c.execute(
            """
            SELECT DISTINCT \"%(col)s\"
            FROM %(table)s
            WHERE \"%(col)s\" IS NOT NULL AND \"%(col)s\" != ''
            ORDER BY \"%(col)s\""""
            % {"col": self.db_column, "table": self.table}
        )
        return [(x, x) for x, in c.fetchall()]

    @classmethod
    def table_search_Q(cls, table, query):
        q = []
        for f in CustomField.objects.filter(is_active=True, table=table, is_searchable=True):
            if f.type == "str":
                q += [{"%s__icontains" % f.name: query}]
            elif f.type == "int":
                if is_int(query):
                    q += [{f.name: int(query)}]
        if q:
            return reduce(lambda x, y: x | models.Q(**y), q, models.Q(**q[0]))
        else:
            return None

    @classmethod
    def on_new_model(cls, sender, *args, **kwargs):
        for f in cls._cfields.get(sender._meta.db_table, []):
            f.install_field()

    @classmethod
    def on_new_document(cls, sender, *args, **kwargs):
        for f in cls._cfields.get(sender._meta.get("collection"), []):
            f.install_field()
