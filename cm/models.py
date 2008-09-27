from django.db import models
from noc.sa.profiles import get_profile_class,profile_choices
from noc.setup.models import Settings
from noc.cm.handlers import get_handler_class,register_handler_classes,handler_choices
from noc.lib.url import URL
from noc.lib.fileutils import rewrite_when_differ,read_file
from noc.cm.vcs import get_vcs
import os,datetime

register_handler_classes()

class ObjectCategory(models.Model):
    class Meta:
        verbose_name="Object Category"
        verbose_name_plural="Object Categories"
    name=models.CharField("Name",max_length=64,unique=True)
    description=models.CharField("Description",max_length=128,null=True,blank=True)
    def __unicode__(self):
        return self.name
#
#
#
class Object(models.Model):
    class Meta:
        verbose_name="Object"
        verbose_name_plural="Objects"
        unique_together=[("handler_class_name","repo_path")]
    handler_class_name=models.CharField("Handler Class",max_length=64,choices=handler_choices)
    stream_url=models.CharField("Stream URL",max_length=128)
    profile_name=models.CharField("Profile",max_length=128,choices=profile_choices)
    repo_path=models.CharField("Repo Path",max_length=128)
    categories=models.ManyToManyField(ObjectCategory,verbose_name="Categories",null=True,blank=True)
    #last_pushed=models.DateTimeField("Last Pushed",blank=True,null=True)
    #last_pulled=models.DateTimeField("Last Pulled",blank=True,null=True)
    
    def __unicode__(self):
        return "%s/%s/%s"%(self.handler_class_name,self.profile_name,self.repo_path)
    
    def _profile(self):
        return get_profile_class(self.profile_name)()
    profile=property(_profile)
    
    def _handler_class(self):
        return get_handler_class(self.handler_class_name)
    handler_class=property(_handler_class)
    
    def _repo(self):
        return os.path.join(Settings.get("cm.repo"),self.handler_class_name)
    repo=property(_repo)
    
    def _path(self):
        return os.path.join(self.repo,self.repo_path)
    path=property(_path)
    
    #
    # If "data" differs from object's content in the repository
    # Write "data" to file and commit
    #
    def write(self,data):
        path=self.path
        is_new=not os.path.exists(path)
        if rewrite_when_differ(self.path,data):
            vcs=get_vcs(self.repo)
            if is_new:
                vcs.add(self.repo_path)
            vcs.commit(self.repo_path)
    #
    # Push object's content from repository to equipment
    #
    def push(self):
        self.handler_class(self).push()
    #
    # Pull object's content into repository
    #
    def pull(self):
        cfg=self.handler_class(self).pull()
        self.write(cfg)
    #
    # Push all objects of the given type
    #
    @classmethod
    def global_push(self,handler_class_name):
        get_handler_class(handler_class_name).global_push()
    #
    # Pull all objects of the given type
    #
    @classmethod
    def global_pull(self,handler_class_name):
        get_handler_class(handler_class_name).global_pull()
    # Returns object's content
    # Or None if no content yet
    def _data(self):
        return read_file(self.path)
    data=property(_data)
    #
    def delete(self):
        vcs=get_vcs(self.repo)
        vcs.rm(self.repo_path)
        super(Object,self).delete()


#
# Load and register all config handlers
#
#register_handler_classes()
