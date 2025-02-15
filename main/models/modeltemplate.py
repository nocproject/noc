# ----------------------------------------------------------------------
# Model Template
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
from noc.core.model.fields import DocumentReferenceField
from noc.core.prettyjson import to_json
from noc.core.model.decorator import on_delete_check
from noc.models import get_model, get_model_id
from noc.inv.models.capability import Capability
from noc.inv.models.resourcegroup import ResourceGroup
from noc.main.models.label import Label
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
    # Remote System map
    mappings: Optional[Dict[str, str]] = None
    # Caps
    user: Optional[Any] = None  # User for changes
    # Send workflow event
    event: Optional[str] = None

    def merge_data(self, ri: "ResourceItem", systems_priority: List[str] = None):
        """Merge data over Multiple Resource Item"""
        if not self.mappings:
            self.mappings = {}
        for m in ri.mappings or {}:
            if m not in self.mappings:
                self.mappings[m] = ri.mappings[m]
        # keys = {(d.name, d.remote_system) for d in self.data}
        data = {d.name: d for d in self.data}
        for d in ri.data:
            if d.name not in data or (not data[d.name].remote_system and d.remote_system):
                # Remote System priority over discovered data
                data[d.name] = d
                continue
            elif (
                not systems_priority
                or not d.remote_system
                or d.remote_system not in systems_priority
            ):
                continue
            elif data[d.name].remote_system not in systems_priority:
                data[d.name] = d
                continue
            i1, i2 = systems_priority.index(d.remote_system), systems_priority.index(
                data[d.name].remote_system
            )
            if i1 > i2:
                data[d.name] = d
        self.data = list(data.values())

    def has_rs_data(self) -> bool:
        """Check remote system data"""
        for d in self.data:
            if d.remote_system:
                return True
        return False


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
    preferred_template_value = BooleanField(default=False)  # Template value override user
    override_existing = BooleanField(default=False)  # Template value

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


@on_delete_check(check=[("sa.ObjectDiscoveryRule", "default_template")])
class ModelTemplate(Document):
    meta = {
        "collection": "modeltemplates",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "main.modeltemplates",
        "json_unique_fields": ["name"],
    }

    name = StringField(unique=True)
    code = StringField()
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
        required=False,
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

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=120)
    _code_cache = cachetools.TTLCache(maxsize=100, ttl=300)

    def __str__(self):
        return f"{self.name} ({self.type})"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ModelTemplate"]:
        return ModelTemplate.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code: str) -> Optional["ModelTemplate"]:
        return ModelTemplate.objects.filter(code=code).first()

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "resource_model": self.resource_model,
            "type": self.type,
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
        env = self.get_env(item, is_new=True)
        if dry_run:
            return
        if not hasattr(self.model_instance, "from_template"):
            raise ValueError("Resource '%s' does not supported Templating" % self.model_instance)
        o = self.model_instance.from_template(**env)
        o.full_clean()
        return o

    def update_instance_data(self, o, item: ResourceItem, dry_run: bool = False) -> bool:
        env = self.get_env(item)
        if not hasattr(o, "update_template_data"):
            raise ValueError("Resource '%s' does not supported Templating" % self.model_instance)
        changed = o.update_template_data(**env)
        if changed:
            o.full_clean()
        if not dry_run:
            o.save()
        return changed

    def get_env(self, item: ResourceItem, is_new: bool = False) -> Dict[str, Any]:
        """
        Build environment from Resource Item:
        * data
        * capabilities
        * resource_groups
        * labels

        Args:
            item: Resource Item
            is_new: Flag for create instance
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
            elif not is_new and not p.override_existing:
                data.pop(p.name, None)
                continue
            elif p.preferred_template_value and p.default_expression and p.name in data:
                r[p.name] = self.normalize_value(params[p.name], p.render_default(**data))
                # May be used in next expression ?
                data.pop(p.name, None)
                continue
            elif p.name not in data and p.default_expression:
                if p.name in params:
                    r[p.name] = self.normalize_value(params[p.name], p.render_default(**data))
                else:
                    r[p.name] = p.render_default(**data)
                continue
            elif p.name not in data:
                continue
            value = data.pop(p.name)
            if p.set_capability:
                caps[str(p.set_capability.id)] = p.set_capability.clean_value(value)
            r[p.param or p.name] = value
        r["labels"] = []
        # Labels
        if item.labels:
            for ll in item.labels:
                # Check allowed set
                if Label.has_model(ll, get_model_id(self.model_instance)):
                    r["labels"].append(ll)
        r["static_service_groups"] = []
        allowed_sg, deny_sg = set(), set()
        for g in self.groups:
            if g.action == "set":
                r["static_service_groups"].append(g.group)
            if not item.service_groups:
                continue
            if g.action == "allow":
                allowed_sg.add(str(g.group.id))
            elif g.action == "deny":
                deny_sg.add(str(g.group.id))
        for g in item.service_groups or []:
            g = ResourceGroup.get_by_id(g)
            if not g:
                print(f"[{g} Unknown ID for Resource Group")
                continue
            if str(g.id) in deny_sg:
                continue
            elif g not in r["static_service_groups"]:
                r["static_service_groups"].append(g)
        for k, v in data.items():
            r[k] = v
        if self.default_state:
            r["state"] = self.default_state
        if self.sticky:
            r["template"] = self
        if item.mappings:
            r["mappings"] = item.mappings
        return r

    def get_model_params(self) -> List[ParamItem]:
        """Get param from Resource Model"""
        r = []
        for field in self.model_instance._meta.fields:
            if isinstance(field, ForeignKey):
                mid = get_model_id(field.remote_field.model)
            elif isinstance(field, DocumentReferenceField):
                mid = (
                    get_model_id(field.document)
                    if not isinstance(field.document, str)
                    else field.document
                )
            else:
                mid = None
            r.append(ParamItem(name=field.name, model_id=mid))
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
