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
from django.db.models.fields.related import ForeignKey
from pydantic import BaseModel
from jinja2 import Template as Jinja2Template

# NOC Modules
from noc.core.mongo.fields import PlainReferenceField
from noc.inv.models.capability import Capability
from noc.inv.models.capsitem import CapsItem
from noc.inv.models.resourcegroup import ResourceGroup
from noc.core.prettyjson import to_json
from noc.models import get_model, get_model_id
from noc.wf.models.state import State


id_lock = threading.Lock()


def check_model(model_name: str):
    try:
        get_model(model_name)
    except AssertionError:
        raise ValidationError


class ParamItem(BaseModel):
    name: str
    model_id: Optional[str] = None
    schema: Optional[Any] = None
    # Schema

    def clean(self, value) -> Any:
        """
        Validate parma

        Args:
            value: Validate Param
        """
        return value


class DataItem(BaseModel):
    name: str
    value: str
    remote_system: Optional[str] = None  # Reference to Resource Group


class ResourceItem(BaseModel):
    """
    Attributes:
        data: Setting data
        labels: List of resource labels
        service_groups: List or Resource groups
        user: User setting data (for manual)
    """

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


class GroupItem(EmbeddedDocument):
    group: ResourceGroup = PlainReferenceField(ResourceGroup, required=True)
    action = StringField(
        choices=[("allow", "Allow"), ("deny", "Deny"), ("set", "Set")], default="allow"
    )
    as_client = BooleanField(default=False)
    as_service = BooleanField(default=True)


class Param(EmbeddedDocument):
    name = StringField(required=True)
    ignore = BooleanField(default=False)  # Ignore field value
    required = BooleanField(default=False)
    hide = BooleanField(default=False)
    default_expression = StringField()
    param = StringField(required=False)
    set_capability: Optional[Capability] = PlainReferenceField(Capability, required=False)
    # preferred_template_value = BooleanField(default=False)  # Template value override user

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            # "preferred_template_value": self.preferred_template_value,
            "ignore": self.ignore,
            "required": self.required,
        }
        if self.param:
            r["param"] = self.param
        if self.set_capability:
            r["set_capability__uuid"] = self.set_capability.uuid
        if self.default_expression:
            r["default_expression"] = self.default_expression
        return r

    def render_default(self, **kwargs):
        return Jinja2Template(self.default_expression).render(kwargs)


class ParamFormItem(EmbeddedDocument):
    # Validate
    name = StringField(required=True)
    hint = StringField()  # Comment for user
    label = StringField()  # Field name
    # is_required = BooleanField(default=False)
    type = StringField(choices=[("integer", "Integer"), ("string", "String")], default="string")
    model_id = StringField()
    validation_method = StringField(choices=["regex", "eq", "choices"])
    validation_expression = StringField()
    validation_range = StringField()

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "type": self.type,
        }
        if self.label:
            r["hint"] = self.label
        if self.hint:
            r["hint"] = self.hint
        if self.validation_method:
            r["validation_method"] = self.validation_method
            r["validation_expression"] = self.validation_expression
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
    # Global ID
    uuid = UUIDField(binary=True, unique=True)
    type = StringField(
        choices=[("host", "Host"), ("service", "Service"), ("resource", "Resource")],
        required=True,
        default="host",
    )
    resource_model = StringField(
        validation=check_model,
        required=True,
        choices=[
            ("vc.Vlan", "Vlan"),
        ],
    )
    params: List[Param] = EmbeddedDocumentListField(Param)
    params_form: List[ParamFormItem] = EmbeddedDocumentListField(ParamFormItem)
    allow_manual = BooleanField(default=False)  # Allow set by User
    sticky: bool = BooleanField(default=False)  # If used, set to resource as template
    groups: List[GroupItem] = EmbeddedDocumentListField(GroupItem)
    labels: List[str] = ListField(StringField())  # Manual Set
    # instances
    default_state: "State" = PlainReferenceField(State)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ResourceTemplate"]:
        return ResourceTemplate.objects.filter(id=oid).first()

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "resource_model": self.resource_model,
            #
            "params": [f.json_data for f in self.params],
            "params_form": [f.json_data for f in self.params_form],
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

    @property
    def model_instance(self):
        if self.type == "host":
            model_id = "sa.ManagedObject"
        elif self.type == "service":
            model_id = "sa.Service"
        else:
            model_id = self.resource_model
        if not model_id:
            raise ValueError("Unknown Resource for Template")
        return get_model(model_id)

    def render(self, item: ResourceItem, dry_run: bool = False):
        """
        Create Resource Instance by item data

        Args:
            item: Param data
            dry_run: Run without create instance (only validate param)
        """
        env = self.get_env(item)
        if dry_run:
            return
        if not hasattr(self.model_instance, "from_template"):
            raise ValueError("Resource '%s' does not supported Templating" % self.model_instance)
        o = self.model_instance.from_template(**env)
        o.full_clean()
        return o

    def get_env(self, item: ResourceItem) -> Dict[str, Any]:
        """
        Build environment from Resource Item:
        * data
        * capabilities
        * resource_groups
        * labels

        Args:
            item: Resource Item
        """
        r: Dict[str, Any] = {}
        caps: Dict[str, Any] = {}
        data: Dict[str, Any] = {}
        params: Dict[str, ParamItem] = {}
        for p in self.get_template_params():
            params[p.name] = p
        for p in self.get_model_params():
            params[p.name] = p
        # Data
        for d in item.data:
            if d.name in params:
                # Validate
                data[d.name] = self.normalize_value(params[d.name], d.value)
            else:
                data[d.name] = d.value
        for p in self.params:
            if p.ignore:
                data.pop(p.name, None)
                continue
            elif p.name not in data and p.required:
                raise ValueError("Parameter %s is required" % p.name)
            elif p.name not in data and p.default_expression:
                r[p.name] = p.render_default(**data)
            elif p.name not in data:
                continue
            value = data.pop(p.name)
            if p.set_capability:
                caps[str(p.set_capability.id)] = p.set_capability.clean_value(value)
            r[p.param or p.name] = value
        # Labels
        if item.labels:
            # Check allowed set
            r["labels"] = list(item.labels)
        r["static_service_groups"] = []
        for g in self.groups:
            if g.action == "set":
                r["static_service_groups"].append(g.group)
            elif g.action == "allow" and str(g.id) in item.service_groups:
                r["static_service_groups"].append(g.group)
            elif g.action == "deny" and str(g.id) in item.service_groups:
                item.service_groups.pop(str(g.id))
        for g in item.service_groups:
            g = ResourceGroup.get_by_id(g)
            if g and g not in r["static_service_groups"]:
                r["static_service_groups"].append(g)
        return r

    def get_model_params(self) -> List[ParamItem]:
        """Get param from Resource Model"""
        r = []
        for field in self.model_instance._meta.fields:
            if isinstance(field, ForeignKey):
                r.append(
                    ParamItem(name=field.name, model_id=get_model_id(field.remote_field.model))
                )
        return r

    def get_template_params(self) -> List[ParamItem]:
        """Get params defined on Template Form Setting"""
        r = []
        for p in self.params_form:
            r.append(ParamItem(name=p.name, model_id=p.model_id))
        return r

    @classmethod
    def normalize_value(cls, param: ParamItem, value: Any) -> Any:
        """
        Normalize and validate param value

        Args:
            param: Param Schema
            value: Param Value
        """
        if param.model_id:
            model = get_model(param.model_id)
            return model.objects.get(id=value)
        return value

    def get_schema(self):
        """Return schema for Web UI"""
