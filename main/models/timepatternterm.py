# ---------------------------------------------------------------------
# TimePatternTerm database model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.timepattern import TimePattern as TP
from noc.core.model.decorator import on_init
from noc.core.change.decorator import change
from .timepattern import TimePattern


@on_init
@change
class TimePatternTerm(NOCModel):
    """
    Time pattern terms
    """

    class Meta(object):
        verbose_name = "Time Pattern Term"
        verbose_name_plural = "Time Pattern Terms"
        db_table = "main_timepatternterm"
        app_label = "main"
        unique_together = [("time_pattern", "term")]

    time_pattern = models.ForeignKey(
        TimePattern, verbose_name="Time Pattern", on_delete=models.CASCADE
    )
    term = models.CharField("Term", max_length=256)

    def __str__(self):
        return "%s: %s" % (self.time_pattern.name, self.term)

    @classmethod
    def get_by_id(cls, id: int) -> Optional["TimePatternTerm"]:
        tpt = TimePatternTerm.objects.filter(id=id)[:1]
        if tpt:
            return tpt[0]
        return None

    @classmethod
    def check_syntax(cls, term):
        """
        Checks Time Pattern syntax. Raises SyntaxError in case of error
        """
        TP(term)

    def save(self, *args, **kwargs):
        """
        Check syntax before save
        """
        TimePatternTerm.check_syntax(self.term)
        super().save(*args, **kwargs)

    def iter_changed_datastream(self, changed_fields=None):
        from noc.sa.models.managedobject import ManagedObject

        for mo in ManagedObject.objects.filter(time_pattern=self.time_pattern):
            yield from mo.iter_changed_datastream(changed_fields=changed_fields)
