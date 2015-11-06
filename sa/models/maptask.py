# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MapTask
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import time
## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models, connection
## NOC modules
from managedobject import ManagedObject
from noc.core.model.fields import PickledField


class MapTask(models.Model):
    class Meta:
        verbose_name = _("Map/Reduce Task Data")
        verbose_name = _("Map/Reduce Task Data")
        db_table = "sa_maptask"
        app_label = "sa"

    task = models.ForeignKey(
        "sa.ReduceTask",
        verbose_name=_("Task"),
        null=True, blank=True,
        on_delete=models.CASCADE
    )
    managed_object = models.ForeignKey(
        ManagedObject,
        verbose_name=_("Managed Object"),
        on_delete=models.CASCADE
    )
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
    # Override script's default timeout
    script_timeout = models.IntegerField(
        _("Script timeout"), null=True, blank=True)
    stop_time = models.DateTimeField(
        _("Stop Time"))

    def __unicode__(self):
        if self.id:
            return u"%d: %s %s" % (
                self.id, self.managed_object, self.map_script)
        else:
            return u"New: %s %s" % (
                self.managed_object, self.map_script)

    @property
    def complete(self):
        return self.status in ("C", "F")

    @classmethod
    def resolve_object(cls, object):
        # Resolve object
        if isinstance(object, basestring):
            return ManagedObject.objects.get(name=object)
        elif isinstance(object, (int, long)):
            return ManagedObject.objects.get(id=object)
        else:
            return object

    @classmethod
    def create_task(cls, object, script, params=None, timeout=None):
        """
        Create single Map task
        :param object: Object name, Object id or Managed Object instance
        :param script: Script name
        :param params: script params
        :param timeout: Timeout in seconds or None for adaptive timeout
        :return:
        """
        status = "W"
        result = None
        # Resolve object
        object = cls.resolve_object(object)
        # Convert script name
        if "." not in script:
            script = "%s.%s" % (object.profile_name, script)
        sp = script.split(".")
        if (len(sp) != 3 or
                not script.startswith(object.profile_name + ".") or
                sp[-1] not in object.profile.scripts):
            status = "F"
            result = {
                "code": ERR_INVALID_SCRIPT,
                "text": "Invalid script %s" % script
            }
        elif not timeout:
            timeout = object.profile.scripts[sp[-1]].get_timeout()
        if not timeout:
            timeout = 60
        now = datetime.datetime.now()
        # Create task
        t = MapTask(
            task=None,
            managed_object=object,
            map_script=script,
            script_params=params,
            next_try=now,
            status=status,
            script_result=result,
            script_timeout=timeout,
            stop_time=now + datetime.timedelta(seconds=timeout)
        )
        t.save()
        return t

    def get_result(self, on_success=None, on_failure=None, block=True):
        """
        Wait for task completion
        :param on_success: Callable acecepting task result which will
            be called on successful completion
        :param on_failure: Callable accepting dict of error code
            and error text to be called on task failure
        :param block:
        :return: True if task completed, False - if still running
        """
        while True:
            t = MapTask.objects.get(id=self.id)
            if t.status == "C":
                # Success
                if on_success:
                    on_success(t.script_result)
                self.delete()
                return True
            elif t.status == "F":
                # Failure
                if on_failure:
                    on_failure(t.script_result)
                self.delete()
                return True
            # Waiting or running
            if not block:
                return False
            time.sleep(1)

    @classmethod
    def run(cls, object, script, params=None, timeout=None):
        from noc.sa.mtmanager import MTManager
        object = cls.resolve_object(object)
        mt = MTManager.run(object, script, params, timeout)
        if mt.status == "C":
            result = mt.script_result
        else:
            result = None
        mt.delete()
        return result
