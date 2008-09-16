from django.db import models
import datetime,random,cPickle

class Task(models.Model):
    class Meta:
        verbose_name="Task"
        verbose_name="Tasks"
    task_id=models.IntegerField("Task",unique=True)
    start_time=models.DateTimeField("Start Time",auto_now_add=True)
    end_time=models.DateTimeField("End Time")
    profile=models.CharField("Profile",max_length=64)
    stream_url=models.CharField("Stream URL",max_length=128)
    action=models.CharField("Action",max_length=64)
    args=models.TextField("Args")
    status=models.CharField("Status",max_length=1,choices=[("n","New"),("p","In Progress"),("f","Failure"),("c","Complete")])
    out=models.TextField("Out")
    def __unicode__(self):
        return u"%d"%self.task_id
    @classmethod
    def create_task(cls,profile,stream_url,action,args={},timeout=600):
        s_time=datetime.datetime.now()
        e_time=s_time+datetime.timedelta(seconds=timeout)
        task_id=random.randint(0,0x7FFFFFFF)
        t=Task(
            task_id=task_id,
            start_time=s_time,
            end_time=e_time,
            profile=profile,
            stream_url=stream_url,
            action=action,
            args=cPickle.dumps(args),
            status="n",
            out="")
        t.save()
        return task_id
        