from django.db import models
from noc.main.report import report_registry
from noc.main.periodic import periodic_registry
import datetime

#
report_registry.register_all()
periodic_registry.register_all()
#
#
#
class TaskSchedule(models.Model):
    periodic_name=models.CharField("Periodic Task",max_length=64,choices=periodic_registry.choices)
    is_enabled=models.BooleanField("Enabled?",default=False)
    run_every=models.PositiveIntegerField("Run Every (secs)",default=86400)
    retries=models.PositiveIntegerField("Retries",default=1)
    retry_delay=models.PositiveIntegerField("Retry Delay (secs)",default=60)
    timeout=models.PositiveIntegerField("Timeout (secs)",default=300)
    next_run=models.DateTimeField("Next Run",auto_now_add=True)
    retries_left=models.PositiveIntegerField("Retries Left",default=1)
    
    def __unicode__(self):
        return self.periodic_name
    
    def _periodic_class(self):
        return periodic_registry[self.periodic_name]
    periodic_class=property(_periodic_class)
    
    @classmethod
    def get_pending_tasks(cls,exclude=None):
        if exclude:
            TaskSchedule.objects.filter(next_run__lte=datetime.datetime.now(),is_enabled=True).exclude(id__in=exclude).order_by("-next_run")
        else:
            return TaskSchedule.objects.filter(next_run__lte=datetime.datetime.now(),is_enabled=True).order_by("-next_run")
    
    @classmethod
    def sleep_timeout(cls,exclude=None):
        if exclude:
            tl=TaskSchedule.objects.filter(next_run__lte=datetime.datetime.now(),is_enabled=True).exclude(id__in=exclude).order_by("-next_run")
        else:
            tl=TaskSchedule.objects.filter(next_run__lte=datetime.datetime.now(),is_enabled=True).order_by("-next_run")
        try:
            t=tl[0]
        except:
            return None
        return (datetime.datetime.now()-t.next_run).seconds

