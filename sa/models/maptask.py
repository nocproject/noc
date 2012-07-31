# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MapTask
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from managedobject import ManagedObject
from reducetask import ReduceTask
from noc.lib.fields import PickledField


class MapTask(models.Model):
    class Meta:
        verbose_name = _("Map/Reduce Task Data")
        verbose_name = _("Map/Reduce Task Data")
        db_table = "sa_maptask"
        app_label = "sa"

    task = models.ForeignKey(ReduceTask, verbose_name=_("Task"))
    managed_object = models.ForeignKey(
        ManagedObject,
        verbose_name=_("Managed Object"))
    map_script = models.CharField(_("Script"), max_length=256)
    script_params = PickledField(_("Params"), null=True, blank=True)
    next_try = models.DateTimeField(_("Next Try"))
    retries_left = models.IntegerField(_("Retries Left"), default=1)
    status = models.CharField(
        _("Status"),
        max_length=1,
        choices=[
            ("W", _("Wait")),
            ("R", _("Running")),
            ("C", _("Complete")),
            ("F", _("Failed"))],
        default="W")
    script_result = PickledField(_("Result"), null=True, blank=True)

    def __unicode__(self):
        if self.id:
            return u"%d: %s %s" % (
                self.id, self.managed_object, self.map_script)
        else:
            return u"New: %s %s" % (
                self.managed_object, self.map_script)
