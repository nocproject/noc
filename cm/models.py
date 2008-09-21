from django.db import models
from noc.sa.profiles import get_profile_class
from noc.setup.models import Settings
from noc.lib.url import URL
from noc.lib.fileutils import rewrite_when_differ,read_file
from noc.cm.vcs import get_vcs
import os,datetime

#
# Global dictionary of object types
#
object_types={}
#
# Register new object type
#
def register_object_type(name,handler_class):
    object_types[name]=handler_class
#
#
#
class ObjectCategory(models.Model):
    class Meta:
        verbose_name="Object Category"
        verbose_name_plural="Object Categories"
    name=models.CharField("Name",max_length=64,unique=True)
    description=models.CharField("Description",max_length=128,null=True,blank=True)
    def __unicode__(self):
        return self.name
#
# URL is in a form:
# <access-schema>://<user>:<password>@<host>:<port>/<object-type>/<in-repo-path>
#
class Object(models.Model):
    class Meta:
        verbose_name="Object"
        verbose_name_plural="Objects"
    url=models.CharField("URL",max_length=128,unique=True)
    profile_name=models.CharField("Profile",max_length=128)
    categories=models.ManyToManyField(ObjectCategory,verbose_name="Categories")
    last_pushed=models.DateTimeField("Last Pushed",blank=True,null=True)
    last_pulled=models.DateTimeField("Last Pulled",blank=True,null=True)
    
    def __unicode__(self):
        return self.url
    
    def _profile(self):
        return get_profile_class(self.profile_name)()
    profile=property(_profile)
    
    def _object_type(self):
        return URL(self.url).path.split("/")[1]
    object_type=property(_object_type)
    
    def _handler_class(self):
        return object_types[self.object_type]
    handler_class=property(_handler_class)
    
    def _path(self):
        return Settings.get("cm.repo")+URL(self.url).path
    path=property(_path)
    
    def _repo(self):
        return os.path.join(Settings.get("cm.repo"),self.object_type)
    repo=property(_repo)
    
    def _repo_path(self):
        return self.path[len(self.repo)+1:]
    repo_path=property(_repo_path)
    
    def push(self):
        self.handler_class(self.profile,self.url).push()
        
    def pull(self):
        cfg=self.handler_class(self.profile,self.url).pull()
        path=self.path
        is_new=not os.path.exists(path)
        if rewrite_when_differ(self.path,cfg):
            vcs=get_vcs(self.repo)
            if is_new:
                vcs.add(self.repo_path)
            vcs.commit(self.repo_path)
        self.last_pulled=datetime.datetime.now()
        self.save()
    # Returns object's content
    # Or None if no content yes
    def _data(self):
        return read_file(self.path)
    data=property(_data)

##
## Object type handler
## Each handler has push and pull methods
##
class Handler(object):
    def __init__(self,profile,stream_url):
        self.profile=profile
        self.stream_url=stream_url
    
    # Prepare configuration changes and push to the equipment
    def push(self):
        pass
    # Grab configuration from equipment
    def pull(self):
        pass
##
## /config/ handler
##
class ConfigHandler(Handler):
    def push(self):
        pass
        
    def pull(self):
        return self.profile.pull_config(self.stream_url)
#
# Register object types
#
register_object_type("config", ConfigHandler)
