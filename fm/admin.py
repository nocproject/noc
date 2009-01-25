from django.contrib import admin
from django import forms
from models import *

class MIBAdmin(admin.ModelAdmin):
    list_display=["name","last_updated","uploaded"]
    search_fields=["name"]

class MIBDataAdmin(admin.ModelAdmin):
    list_display=["mib","oid","name"]
    search_fields=["oid","name"]

admin.site.register(MIB, MIBAdmin)
admin.site.register(MIBData, MIBDataAdmin)

