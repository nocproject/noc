# ----------------------------------------------------------------------
# Group model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional
import operator

# Third-party modules
import cachetools
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@on_delete_check(
    check=[
        ("sa.GroupAccess", "group"),
        ("main.AuthLDAPDomain", "groups__group"),
        ("aaa.ModelProtectionProfile", "groups"),
    ]
)
class Group(NOCModel):
    class Meta(object):
        verbose_name = "Group"
        verbose_name_plural = "Groups"
        app_label = "aaa"
        # Point to django"s auth_user table
        db_table = "auth_group"
        ordering = ["name"]

    name = models.CharField(max_length=80, unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["Group"]:
        return Group.objects.filter(id=id).first()
