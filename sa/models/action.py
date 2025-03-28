# ----------------------------------------------------------------------
# Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import threading
import operator
from typing import Any, Dict, Optional, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    IntField,
    BooleanField,
    ListField,
    EmbeddedDocumentField,
)
import jinja2
import cachetools

# NOC modules
from noc.core.text import quote_safe_path
from noc.core.prettyjson import to_json
from noc.core.ip import IP
from noc.core.model.decorator import on_delete_check

id_lock = threading.Lock()


class ActionParameter(EmbeddedDocument):
    name = StringField()
    type = StringField(
        choices=[
            ("int", "int"),
            ("float", "float"),
            ("str", "str"),
            ("interface", "interface"),
            ("ip", "ip"),
            ("vrf", "vrf"),
        ]
    )
    description = StringField()
    is_required = BooleanField(default=True)
    default = StringField()

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "is_required": self.is_required,
        }
        if self.default is not None:
            r["default"] = self.default
        return r


@on_delete_check(
    check=[
        ("sa.ActionCommands", "action"),
        ("fm.DispositionRule", "object_actions.action"),
        ("fm.AlarmDiagnosticConfig", "on_clear_action"),
        ("fm.AlarmDiagnosticConfig", "periodic_action"),
        ("fm.AlarmDiagnosticConfig", "on_raise_action"),
    ]
)
class Action(Document):
    meta = {
        "collection": "noc.actions",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "sa.actions",
    }
    uuid = UUIDField(unique=True)
    name = StringField(unique=True)
    label = StringField()
    description = StringField()
    access_level = IntField(default=15)
    # Optional handler for non-sa actions
    handler = StringField()
    #
    params = ListField(EmbeddedDocumentField(ActionParameter))

    _id_cache = cachetools.TTLCache(1000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Action"]:
        return Action.objects.filter(id=oid).first()

    def get_json_path(self) -> str:
        return "%s.json" % quote_safe_path(self.name)

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "label": self.label,
            "description": self.description,
            "access_level": self.access_level,
        }
        if self.handler:
            r["handler"] = self.handler
        r["params"] = [c.json_data for c in self.params]
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "label",
                "description",
                "access_level",
                "handler",
                "params",
            ],
        )

    def get_commands(self, obj):
        """
        Returns ActionCommands instance or None
        :param obj: Managed Object
        """
        from .actioncommands import ActionCommands

        for ac in ActionCommands.objects.filter(action=self, profile=obj.profile.id).order_by(
            "preference"
        ):
            if not ac.match:
                return ac
            for m in ac.match:
                if (
                    not m.platform_re
                    or (obj.platform and re.search(m.platform_re, obj.platform.name))
                ) and (
                    not m.version_re
                    or (obj.version and re.search(m.version_re, obj.version.version))
                ):
                    return ac
        return None

    def expand_ex(self, obj, **kwargs):
        ac = self.get_commands(obj)
        if not ac:
            return None, None
        # Render template
        loader = jinja2.DictLoader({"tpl": ac.commands})
        env = jinja2.Environment(loader=loader)
        template = env.get_template("tpl")
        return ac, template.render(**self.clean_args(obj, **kwargs))

    def expand(self, obj, **kwargs):
        return self.expand_ex(obj, **kwargs)[1]

    def execute(self, obj, **kwargs):
        """
        Execute commands
        """
        ac, commands = self.expand_ex(obj, **kwargs)
        if commands is None:
            return None
        # Execute rendered commands
        if ac.config_mode:
            return obj.scripts.configure(commands=commands)
        else:
            return obj.scripts.commands(commands=commands)

    def clean_args(self, obj, **kwargs):
        args = {}
        for p in self.params:
            if p.name not in kwargs and p.is_required and not p.default:
                raise ValueError("Required parameter '%s' is missed" % p.name)
            v = kwargs.get(p.name, p.default)
            if v is None:
                continue
            if p.type == "int":
                # Integer type
                try:
                    v = int(v)
                except ValueError:
                    raise ValueError("Invalid integer in parameter '%s': '%s'" % (p.name, v))
            elif p.type == "float":
                # Float type
                try:
                    v = float(v)
                except ValueError:
                    raise ValueError("Invalid float in parameter '%s': '%s'" % (p.name, v))
            elif p.type == "interface":
                # Interface
                try:
                    v = obj.get_profile().convert_interface_name(v)
                except Exception:
                    raise ValueError("Invalid interface name in parameter '%s': '%s'" % (p.name, v))
            elif p.type == "ip":
                # IP address
                try:
                    v = IP.prefix(v)
                except ValueError:
                    raise ValueError("Invalid ip in parameter '%s': '%s'" % (p.name, v))
            elif p.type == "vrf":
                if isinstance(v, VRF):
                    pass
                elif isinstance(v, int):
                    try:
                        v = VRF.objects.get(id=v)
                    except VRF.DoesNotExist:
                        raise ValueError("Unknown VRF in parameter '%s': '%s'" % (p.name, v))
                elif isinstance(v, str):
                    try:
                        v = VRF.objects.get(name=v)
                    except VRF.DoesNotExist:
                        raise ValueError("Unknown VRF in parameter '%s': '%s'" % (p.name, v))
                else:
                    raise ValueError("Unknown VRF in parameter '%s': '%s'" % (p.name, v))
            args[str(p.name)] = v
        return args


#
from noc.ip.models.vrf import VRF
