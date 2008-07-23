from django.db import models
from django.core.cache import cache

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

D=[
    ("shell.ssh",   "/usr/bin/ssh"),
    ("shell.rsync", "/usr/local/bin/rsync"),
    # Trouble ticketing integratiion
    ("tt.url",      "http://example.com/ticket=%(tt)s"),
    # dns
    ("dns.zone_cache",  "/tmp/zones/"),
    ("dns.rsync_target","user@host:/path/"),
]

def register_defaults():
    for k,v in D:
        Settings.register(k,v)