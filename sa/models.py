from django.db import models
import datetime,random,cPickle,time
from noc.sa.profiles import profile_registry
from noc.sa.periodic import periodic_registry

profile_registry.register_all()
periodic_registry.register_all()

class Activator(models.Model):
    class Meta:
        verbose_name="Activator"
        verbose_name_plural="Activators"
    name=models.CharField("Name",max_length=32,unique=True)
    ip=models.IPAddressField("IP")
    auth=models.CharField("Auth String",max_length=64)
    is_active=models.BooleanField("Is Active",default=True)
    def __unicode__(self):
        return self.name

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


class Task(models.Model):
    class Meta:
        verbose_name="Task"
        verbose_name_plural="Tasks"
    task_id=models.IntegerField("Task",unique=True)
    start_time=models.DateTimeField("Start Time",auto_now_add=True)
    end_time=models.DateTimeField("End Time")
    profile_name=models.CharField("Profile",max_length=64,choices=profile_registry.choices)
    stream_url=models.CharField("Stream URL",max_length=128)
    action=models.CharField("Action",max_length=64)
    args=models.TextField("Args")
    status=models.CharField("Status",max_length=1,choices=[("n","New"),("p","In Progress"),("f","Failure"),("c","Complete")])
    out=models.TextField("Out")
    def __unicode__(self):
        return u"%d"%self.task_id
    @classmethod
    def create_task(cls,profile_name,stream_url,action,args={},timeout=600):
        # Check profile exists
        profile_registry[profile_name]
        #
        s_time=datetime.datetime.now()
        e_time=s_time+datetime.timedelta(seconds=timeout)
        task_id=random.randint(0,0x7FFFFFFF)
        t=Task(
            task_id=task_id,
            start_time=s_time,
            end_time=e_time,
            profile_name=profile_name,
            stream_url=stream_url,
            action=action,
            args=cPickle.dumps(args),
            status="n",
            out="")
        t.save()
        return task_id
    def _profile(self):
        return profile_registry[self.profile_name]()
    profile=property(_profile)
    
def get_task_output(profile_name,stream_url,action,args={},timeout=600):
    task_id=Task.create_task(profile_name,stream_url,action,args,timeout)
    while True:
        time.sleep(1)
        task=Task.objects.get(task_id=task_id)
        if task.status=="c":
            out=task.out
            task.delete()
            return out
        elif task.status=="f":
            out=task.out
            task.delete()
            raise Exception(out)