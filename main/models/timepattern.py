# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# TimePattern database model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import operator
# Python modules
from threading import Lock

# Third-party modules
import cachetools
from django.db import models
from noc.core.model.decorator import on_delete_check
# NOC modules
from noc.lib.timepattern import TimePattern as TP

id_lock = Lock()


@on_delete_check(check=[
    # ("fm.EscalationItem", "administrative_domain")
    ("fm.AlarmTrigger", "time_pattern"),
    ("fm.EventTrigger", "time_pattern"),
    ("main.Schedule", "time_pattern"),
    ("main.TimePatternTerm", "time_pattern"),
    ("maintenance.Maintenance", "time_pattern"),
    ("sa.ManagedObject", "time_pattern")
])
class TimePattern(models.Model):
    """
    Time Patterns
    """

    class Meta:
        verbose_name = "Time Pattern"
        verbose_name_plural = "Time Patterns"
        db_table = "main_timepattern"
        app_label = "main"

    name = models.CharField("Name", max_length=64, unique=True)
    description = models.TextField("Description", null=True, blank=True)

    _code_cache = cachetools.TTLCache(1000, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
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
        else:
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
