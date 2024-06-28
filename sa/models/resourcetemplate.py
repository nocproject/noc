# ----------------------------------------------------------------------
# Resource Template
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import operator
from typing import Optional, Dict, List, Any, Union

# Third-party modules
import cachetools
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    UUIDField,
    EmbeddedDocumentListField,
)
from mongoengine.errors import ValidationError
from pydantic import BaseModel

# NOC Modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.etl.loader.loader import loader
from noc.core.etl.loader.base import BaseLoader
from noc.core.prettyjson import to_json
from noc.models import get_model
from noc.wf.models.state import State


class DataItem(BaseModel):
    name: str
    value: str
    remote_system: Optional[str] = None  # Reference to Resource Group


class ResourceItem(BaseModel):
    """"""

    data: List[DataItem]
    id: Optional[str] = None
    labels: Optional[List[str]] = None
    service_groups: Optional[List[str]] = None
    # Caps
    user: Optional[Any] = None  # User for changes


class Result(BaseModel):
    id: Optional[str] = None
    status: bool = True
    error: Optional[str] = None
    error_code: Optional[str] = None
    error_fields: List[str] = None


id_lock = threading.Lock()


def check_model(model_name: str):
    try:
        get_model(model_name)
    except AssertionError:
        raise ValidationError


class Field(EmbeddedDocument):
    # Validate
    name = StringField(required=True)
    hint = StringField()  # Comment for user
    # is_required = BooleanField(default=False)
    preferred_template_value = BooleanField(default=False)  # Template value override user
    ignore = BooleanField(default=False)  # Ignore field value
    validation_method = StringField(choices=["regex", "eq", "range", "choices"])
    validation_expression = StringField()
    default_expression = StringField()

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "preferred_template_value": self.preferred_template_value,
            "ignore": self.ignore,
        }
        if self.hint:
            r["hint"] = self.hint
        if self.validation_method:
            r["validation_method"] = self.validation_method
            r["validation_expression"] = self.validation_expression
        if self.default_expression:
            r["default_expression"] = self.default_expression
        return r


class ResourceTemplate(Document):
    meta = {
        "collection": "resourcetemplates",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "sa.resourcetemplates",
        "json_unique_fields": ["name"],
    }

    name = StringField(unique=True)
    description = StringField()
    resource = StringField(
        validation=check_model,
        required=True,
        choices=[
            ("sa.ManagedObject", "managed_object"),
        ],
    )
    # Global ID
    uuid = UUIDField(binary=True)
    type = StringField(
        choices=[("global", "Global"), ("discovery", "Discovery")],
        required=True,
    )
    fields: List[Field] = EmbeddedDocumentListField(Field)
    allow_manual = BooleanField(default=False)  # Allow set by User
    sticky: bool = BooleanField(default=False)  # If used, set to resource as template
    labels: List[str] = ListField(StringField())  # Manual Set
    # groups
    default_state: "State" = PlainReferenceField(State)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ResourceTemplate"]:
        return ResourceTemplate.objects.filter(id=oid).first()

    @property
    def model_instance(self):
        return get_model(self.resource)

    def get_etl_loader(self, name="managedobject") -> Optional["BaseLoader"]:
        return loader.get_loader(name)

    def normalize_value(self, field: DataItem, setting: Field) -> str:
        mapped_fields = self.get_etl_loader().data_model.get_mapped_fields()
        if field.remote_system and field.name in mapped_fields:
            model = self.get_etl_loader(mapped_fields[field.name]).model
            value = model.objects.filter(
                remote_system=field.remote_system, remote_id=field.value
            ).first()
        else:
            value = field.value
        return value or setting.default_expression

    def get_fields(self):
        r = {}
        for f in self.model_instance._meta.fields:
            r[f.name] = f
        return r

    def get_kwargs(self, record: ResourceItem) -> Dict[str, Any]:
        """Convert Data to Context"""
        fields = self.get_fields()
        r = {}
        settings = {}
        for f in self.fields:
            settings[f.name] = f
        for d in record.data:
            if d.name not in fields:
                continue
            value = self.normalize_value(d, settings.pop(d.name, None))
            if not value:
                continue
            r[d.name] = value
        for f, s in settings.items():
            if s.default_expression:
                r[f] = s.default_expression
        if record.labels:
            r["labels"] = record.labels
        return r

    def get_instance(self, **kwargs) -> Any:
        """Create instance for context"""
        model = get_model(self.resource)
        return model(**kwargs)

    def get_schema(self):
        """Return schema for Web UI"""

    def run(self, data: List[ResourceItem], dry_run=False) -> List[Result]:
        r = []
        for d in data:
            ctx = self.get_kwargs(d)
            try:
                o = self.get_instance(**ctx)
                o.full_clean()
                if not dry_run:
                    o.save()
            except ValidationError as e:
                r.append(Result(status=False, error=str(e)))
                continue
            r.append(Result(id=str(o.id)))
        return r

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "resource": self.resource,
            #
            "fields": [f.json_data for f in self.fields],
            #
            "allow_manual": self.allow_manual,
            "sticky": self.sticky,
        }
        if self.default_state:
            r["default_state__uuid"] = str(self.default_state.uuid)
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
            ],
        )
