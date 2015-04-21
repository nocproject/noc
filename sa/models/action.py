# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Action
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import time
## Django modules
from django.template import Template, Context
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, UUIDField, IntField,
                                BooleanField, ListField,
                                EmbeddedDocumentField)
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json
##

class ActionParameter(EmbeddedDocument):
    name = StringField()
    type = StringField(
        choices=[
            ("int", "int"),
            ("float", "float"),
            ("str", "str"),
            ("interface", "interface")
        ]
    )
    description = StringField()
    is_required = BooleanField(default=True)

    def __unicode__(self):
        return self.name

    @property
    def json_data(self):
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "is_required": self.is_required
        }


class Action(Document):
    meta = {
        "collection": "noc.actions",
        "json_collection": "sa.actions"
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

    def __unicode__(self):
        return self.name

    def get_json_path(self):
        return "%s.json" % quote_safe_path(self.name)

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "uuid": self.uuid,
            "label": self.label,
            "description": self.description,
            "access_level": self.access_level
        }
        if self.handler:
            r["handler"] = self.handler
        r["params"] = [c.json_data for c in self.params]
        return r

    def to_json(self):
        return to_json(self.json_data,
                       order=["name", "uuid", "label",
                              "description",
                              "access_level",
                              "handler",
                              "params"])

    def get_commands(self, obj):
        """
        Returns ActionCommands instance or None
        :param obj: Managed Object
        """
        version = obj.version
        for ac in ActionCommands.objects.filter(action=self).order_by("preference"):
            if not ac.match:
                return ac
            for m in ac.match:
                if (
                    not m.platform_re or (
                        version.platform and
                        re.search(m.platform_re, version.platform)
                    )
                ) and (
                    not m.version_re or (
                        version.version and
                        re.search(m.version_re, version.version))
                ):
                    return ac
        return None

    def execute(self, obj, **kwargs):
        """
        Execute commands
        """
        ac = self.get_commands(obj)
        if not ac:
            return None
        ctx = Context(self.clean_args(obj, **kwargs))
        commands = Template(ac.commands).render(ctx)
        t = MapTask.create_task(obj, "commands", {
            "commands": commands.splitlines()
        }, timeout=ac.timeout)
        while True:
            t = MapTask.objects.get(id=t.id)
            if t.status == "C":
                # Success
                t.delete()
                result = t.script_result
                if isinstance(result, list):
                    result = "\n".join(result)
                return result
            elif t.status == "F":
                # Failure
                t.delete()
                return t.script_result
            time.sleep(1)

    def clean_args(self, obj, **kwargs):
        args = {}
        for p in self.params:
            if not p.name in kwargs and p.is_required:
                raise ValueError(
                    "Required parameter '%s' is missed" % p.name
                )
            v = kwargs[p.name]
            if p.type == "int":
                # Integer type
                try:
                    v = int(v)
                except ValueError, why:
                    raise ValueError(
                        "Invalid integer in parameter '%s': '%s'" % (
                            p.name, v)
                    )
            elif p.type == "float":
                # Float type
                try:
                    v = float(v)
                except ValueError, why:
                    raise ValueError(
                        "Invalid float in parameter '%s': '%s'" % (
                            p.name, v)
                    )
            elif p.type == "interface":
                # Interface
                try:
                    v = obj.profile.convert_interface_name(v)
                except Exception, why:
                    raise ValueError(
                        "Invalid interface name in parameter '%s': '%s'" % (
                            p.name, v)
                    )
            args[p.name] = v
        return args


##
from actioncommands import ActionCommands
from maptask import MapTask