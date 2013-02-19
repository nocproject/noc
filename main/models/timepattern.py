# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TimePattern database model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
from noc.lib.timepattern import TimePattern as TP


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

    def __unicode__(self):
        return self.name

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
