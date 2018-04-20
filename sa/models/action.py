# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import re
import threading
import operator
# Third-party modules
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, UUIDField, IntField,
                                BooleanField, ListField,
                                EmbeddedDocumentField)
<<<<<<< HEAD
import six
import jinja2
import cachetools
# NOC modules
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json
from noc.core.ip import IP

id_lock = threading.Lock()
=======
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json
from noc.lib.ip import IP
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class ActionParameter(EmbeddedDocument):
    name = StringField()
    type = StringField(
        choices=[
            ("int", "int"),
            ("float", "float"),
            ("str", "str"),
            ("interface", "interface"),
            ("ip", "ip"),
            ("vrf", "vrf")
        ]
    )
    description = StringField()
    is_required = BooleanField(default=True)
    default = StringField()

    def __unicode__(self):
        return self.name

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "is_required": self.is_required
        }
        if self.default is not None:
            r["default"] = self.default
        return r


class Action(Document):
    meta = {
        "collection": "noc.actions",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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

<<<<<<< HEAD
    _id_cache = cachetools.TTLCache(1000, ttl=60)
    
    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Action.objects.filter(id=id).first()

=======
    def __unicode__(self):
        return self.name

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def get_json_path(self):
        return "%s.json" % quote_safe_path(self.name)

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
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
                       order=["name", "$collection", "uuid", "label",
                              "description",
                              "access_level",
                              "handler",
                              "params"])

    def get_commands(self, obj):
        """
        Returns ActionCommands instance or None
        :param obj: Managed Object
        """
<<<<<<< HEAD
        from .actioncommands import ActionCommands
        for ac in ActionCommands.objects.filter(
                action=self, profile=obj.profile.id
=======
        version = obj.version
        for ac in ActionCommands.objects.filter(
                action=self, profile=obj.profile_name
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        ).order_by("preference"):
            if not ac.match:
                return ac
            for m in ac.match:
                if (
                    not m.platform_re or (
<<<<<<< HEAD
                        obj.platform and
                        re.search(m.platform_re, obj.platform.name)
                    )
                ) and (
                    not m.version_re or (
                        obj.version and
                        re.search(m.version_re, obj.version.version))
=======
                        version.platform and
                        re.search(m.platform_re, version.platform)
                    )
                ) and (
                    not m.version_re or (
                        version.version and
                        re.search(m.version_re, version.version))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                ):
                    return ac
        return None

<<<<<<< HEAD
    def expand(self, obj, **kwargs):
        ac = self.get_commands(obj)
        if not ac:
            return None
        # Render template
        loader = jinja2.DictLoader({"tpl": ac.commands})
        env = jinja2.Environment(loader=loader)
        template = env.get_template("tpl")
        return template.render(**self.clean_args(obj, **kwargs))

=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute(self, obj, **kwargs):
        """
        Execute commands
        """
<<<<<<< HEAD
        commands = self.expand(obj, **kwargs)
        if commands is None:
            return None
        # Execute rendered commands
        if ac.config_mode:
            return obj.scripts.configure(commands=commands)
        else:
            return obj.scripts.commands(commands=commands)
=======
        ac = self.get_commands(obj)
        if not ac:
            return None
        ctx = Context(self.clean_args(obj, **kwargs))
        commands = Template(ac.commands).render(ctx)
        script = "configure" if ac.config_mode else "commands"
        t = MapTask.create_task(obj, script, {
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def clean_args(self, obj, **kwargs):
        args = {}
        for p in self.params:
            if not p.name in kwargs and p.is_required and not p.default:
                raise ValueError(
                    "Required parameter '%s' is missed" % p.name
                )
            v = kwargs.get(p.name, p.default)
            if v is None:
                continue
            if p.type == "int":
                # Integer type
                try:
                    v = int(v)
<<<<<<< HEAD
                except ValueError:
=======
                except ValueError, why:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    raise ValueError(
                        "Invalid integer in parameter '%s': '%s'" % (
                            p.name, v)
                    )
            elif p.type == "float":
                # Float type
                try:
                    v = float(v)
<<<<<<< HEAD
                except ValueError:
=======
                except ValueError, why:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    raise ValueError(
                        "Invalid float in parameter '%s': '%s'" % (
                            p.name, v)
                    )
            elif p.type == "interface":
                # Interface
                try:
<<<<<<< HEAD
                    v = obj.get_profile().convert_interface_name(v)
                except Exception:
=======
                    v = obj.profile.convert_interface_name(v)
                except Exception, why:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    raise ValueError(
                        "Invalid interface name in parameter '%s': '%s'" % (
                            p.name, v)
                    )
            elif p.type == "ip":
                # IP address
                try:
                    v = IP.prefix(v)
<<<<<<< HEAD
                except ValueError:
=======
                except ValueError, why:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    raise ValueError(
                        "Invalid ip in parameter '%s': '%s'" % (p.name, v)
                    )
            elif p.type == "vrf":
                if isinstance(v, VRF):
                    pass
<<<<<<< HEAD
                elif isinstance(v, six.integer_types):
=======
                elif isinstance(v, (int, long)):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    try:
                        v = VRF.objects.get(id=v)
                    except VRF.DoesNotExist:
                        raise ValueError(
                            "Unknown VRF in parameter '%s': '%s'" % (p.name, v)
                        )
<<<<<<< HEAD
                elif isinstance(v, six.string_types):
=======
                elif isinstance(v, basestring):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    try:
                        v = VRF.objects.get(name=v)
                    except VRF.DoesNotExist:
                        raise ValueError(
                            "Unknown VRF in parameter '%s': '%s'" % (p.name, v)
                        )
                else:
                    raise ValueError(
                        "Unknown VRF in parameter '%s': '%s'" % (p.name, v)
                    )
            args[str(p.name)] = v
        return args


<<<<<<< HEAD
#
from noc.ip.models.vrf import VRF
=======
##
from actioncommands import ActionCommands
from maptask import MapTask
from noc.ip.models.vrf import VRF
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
