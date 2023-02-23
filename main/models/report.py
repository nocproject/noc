# ---------------------------------------------------------------------
# Report model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, Any

# Third-party modules
from mongoengine.document import Document
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    EmbeddedDocumentListField,
    BooleanField,
    ListField,
    DictField,
    FileField,
)

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from noc.aaa.models.user import User
from noc.aaa.models.group import Group


class ReportParam(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField(required=True)
    description = StringField(required=False)
    label = StringField()
    type = StringField(choices=["integer", "string", "date", "model"], required=True)
    model_id = StringField()
    required = BooleanField(default=False)
    default = StringField(required=False)
    localization = DictField()

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"name": self.name, "description": self.description}
        if self.default:
            r["default"] = self.default
        return r


class Template(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    output_type = StringField()
    code = StringField(default="DEFAULT")
    formatter = StringField()
    content = FileField(required=False)
    output_name_pattern = StringField()
    handler = StringField()


class Query(EmbeddedDocument):
    datasource = StringField()
    ds_query = StringField()
    json = StringField()


class BandFormat(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField(required=True)
    title_template = StringField()
    column_format = ListField(DictField())


class Band(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField()
    parent = StringField()
    orientation = StringField(choices=["H", "V", "C", "U"])
    queries = EmbeddedDocumentListField(Query)


class Permission(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)
    edit = BooleanField(default=True)  # Edit report settings
    launch = BooleanField(default=False)  # Run to


class Report(Document):
    meta = {
        "collection": "noc.reports",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "main.reportes",
        "json_unique_fields": ["name"],
    }

    # Report name
    name = StringField(required=True, unique=True)
    category = StringField()
    uuid = UUIDField(binary=True)
    description = StringField(required=False)
    #
    code = StringField()  # Optional code for REST access
    hide = BooleanField()  # Hide from ReportMenu
    is_system = BooleanField(default=False)  # Report Is System Based
    allow_rest = BooleanField(default=False)   # Available report data from REST API
    #
    parameters = EmbeddedDocumentListField(ReportParam)
    templates = EmbeddedDocumentListField(Template)
    bands = EmbeddedDocumentListField(Band)
    bands_format = EmbeddedDocumentListField(BandFormat)
    #
    permissions = EmbeddedDocumentListField(Permission)
    localization = DictField()
