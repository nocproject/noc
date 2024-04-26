# ---------------------------------------------------------------------
# Template model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Dict, Any
import operator

# Third-party modules
from django.db import models
from django.core.exceptions import ValidationError
import jinja2
import cachetools

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_delete_check
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path

id_lock = Lock()


def template_validator(value):
    if not value:
        return
    try:
        jinja2.Template(value)
    except jinja2.exceptions.TemplateSyntaxError as e:
        raise ValidationError(str(e))


@on_delete_check(
    check=[
        ("fm.AlarmTrigger", "template"),
        ("fm.ActiveAlarm", "clear_template"),
        ("fm.EventTrigger", "template"),
        ("inv.NetworkSegmentProfile", "calcified_name_template"),
        ("ip.AddressProfile", "name_template"),
        ("ip.AddressProfile", "fqdn_template"),
        ("ip.PrefixProfile", "name_template"),
        ("main.SystemTemplate", "template"),
        ("main.MessageRoute", "transmute_template"),
        ("main.MessageRoute", "render_template"),
        ("sa.AdministrativeDomain", "bioseg_floating_name_template"),
        ("sa.ManagedObjectProfile", "beef_path_template"),
        ("sa.ManagedObjectProfile", "config_mirror_template"),
        ("sa.ManagedObjectProfile", "config_download_template"),
        ("vc.VPNProfile", "name_template"),
        ("maintenance.Maintenance", "template"),
    ]
)
class Template(NOCModel):
    class Meta(object):
        app_label = "main"
        db_table = "main_template"
        verbose_name = "Template"
        verbose_name_plural = "Templates"
        ordering = ["name"]

    meta = {"collection": "templates", "json_collection": "main.templates"}

    name = models.CharField("Name", unique=True, max_length=128)
    subject = models.TextField("Subject", validators=[template_validator])
    body = models.TextField("Body", validators=[template_validator])
    uuid = models.UUIDField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "uuid": self.uuid,
            "$collection": self.meta["json_collection"],
            "name": self.name,
            "subject": self.subject,
            "body": self.body,
        }
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "uuid",
                "$collection",
                "name",
                "subject",
                "body",
            ],
        )

    def get_json_path(self) -> str:
        return quote_safe_path(self.name.strip("*")) + ".json"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["Template"]:
        t = Template.objects.filter(id=id)[:1]
        if t:
            return t[0]
        return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        t = Template.objects.filter(name=name)[:1]
        if t:
            return t[0]
        return None

    def render_subject(self, LANG=None, **kwargs):
        return jinja2.Template(self.subject).render(**kwargs)

    def render_body(self, LANG=None, **kwargs):
        return jinja2.Template(self.body).render(**kwargs)
