from django.db import models
from django.core.cache import cache

class Settings(models.Model):
    class Admin:
        list_display=["key","value","default"]
        search_fields=["key","value"]
    class Meta:
        verbose_name="Settings"
        verbose_name_plural="Settings"
    key=models.CharField("Key",max_length=64,unique=True)
    value=models.CharField("Value",max_length=256)
    default=models.CharField("Default",max_length=256)
    def __str__(self):
        return self.key
    def __unicode__(self):
        return unicode(self.key)
    @classmethod
    def get(cls,v):
        key="settings.%s"%v
        c=cache.get(key)
        if c is None:
            c=Settings.objects.get(key=v).value
            cache.set(key,c)
        return c
    @classmethod
    def register(cls,key,default):
        if Settings.objects.filter(key=key).count()==0:
            s=Settings(key=key,value=default,default=default)
            s.save()
    @classmethod
    def unregister(cls,key,default):
        if Settings.objects.filter(key=key).count()==1:
            s=Settings.objects.get(key=key)
            if s.value==s.default:
                s.delete()
    @classmethod
    def migration_forward(self,lst):
        for k,v in lst:
            Settings.register(k,v)
    @classmethod
    def migration_backward(self,lst):
        for k,v in lst:
            Settings.unregister(k,v)

