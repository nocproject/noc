from django.db import models

class Settings(models.Model):
    class Admin:
        list_display=["key","value","default"]
        search_fields=["key","value"]
    key=models.CharField("Key",maxlength=64,unique=True)
    value=models.CharField("Value",maxlength=256)
    default=models.CharField("Value",maxlength=256)
    def __str__(self):
        return self.key
    def __unicode__(self):
        return unicode(self.key)
    @classmethod
    def __getitem__(cls,v):
        return Settings.objects.get(key=v).value
    @classmethod
    def register(cls,key,default):
        if Settings.objects.filter(key=key).count()==0:
            s=Settings(key=key,value=default,default=default)
            s.save()

