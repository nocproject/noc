# ---------------------------------------------------------------------
# TimePattern database model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional
import operator

# Third-party modules
import cachetools
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.timepattern import TimePattern as TP
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@on_delete_check(
    check=[
        # ("fm.EscalationItem", "administrative_domain")
        ("aaa.UserContact", "time_pattern"),
        ("fm.AlarmTrigger", "time_pattern"),
        ("fm.EventTrigger", "time_pattern"),
        ("main.TimePatternTerm", "time_pattern"),
        ("main.NotificationGroupUser", "time_pattern"),
        ("main.NotificationGroupOther", "time_pattern"),
        ("maintenance.Maintenance", "time_pattern"),
        ("sa.ManagedObject", "time_pattern"),
    ]
)
class TimePattern(NOCModel):
    """
    Time Patterns
    """

    class Meta(object):
        verbose_name = "Time Pattern"
        verbose_name_plural = "Time Patterns"
        db_table = "main_timepattern"
        app_label = "main"

    name = models.CharField("Name", max_length=64, unique=True)
    description = models.TextField("Description", null=True, blank=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _code_cache = cachetools.TTLCache(1000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["TimePattern"]:
        p = TimePattern.objects.filter(id=id)[:1]
        if p:
            return p[0]
        else:
            return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_code(cls, id):
        p = TimePattern.get_by_id(id)
        if p:
            return TP.compile_to_python([t.term for t in p.timepatternterm_set.all()])
        return None

    @property
    def time_pattern(self):
        """
        Returns associated Time Pattern object
        """
        return TP([t.term for t in self.timepatternterm_set.all()])

    def match(self, d):
        """
        Matches DateTime objects against time pattern
        """
        return self.time_pattern.match(d)


# Avoid circular references
# No delete, fixed 'TimePattern' object has no attribute 'timepatternterm_set'
from .timepatternterm import TimePatternTerm  # noqa
