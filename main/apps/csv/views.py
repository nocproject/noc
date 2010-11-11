# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CSV Export/Import application
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.db import transaction
## NOC modules
from noc.lib.app import Application,HasPerm
from noc.lib.csvutils import csv_export,csv_import,get_model_fields
##
##
##
class CSVApplication(Application):
    title="CSV Export/Import"
    ##
    ## CSV Import form
    ##
    class ImportForm(forms.Form):
        file=forms.FileField()
        referer=forms.CharField(widget=forms.HiddenInput)
    ##
    ## Import from CSV file
    ##
    def view_import(self,request,model):
        a,m=model.split(".")
        m=get_object_or_404(ContentType,app_label=a,model=m).model_class()
        if request.POST:
            form=self.ImportForm(request.POST, request.FILES)
            if form.is_valid():
                count,error=csv_import(m,request.FILES['file'])
                if error:
                    # Rollback current transaction to be able to send message
                    transaction.rollback()
                if count is None:
                    self.message_user(request,"Error imporing data: %s"%error)
                else:
                    self.message_user(request,"%d records are imported/updated"%count)
                return self.response_redirect(form.cleaned_data["referer"])
        else:
            form=self.ImportForm({"referer":request.META.get("HTTP_REFERER","/")})
        # Prepare fields description
        fields=[]
        for name,required,rel,rname in get_model_fields(m):
            if rel:
                db_table=rel._meta.db_table
                r=["%s.\"id\""%db_table]
                if rname!="id":
                    r=["%s.\"%s\""%(db_table,rname)]+r
            else:
                r=[]
            fields+=[(name,required," or ".join(r))]
        return self.render(request,"import.html",{"form":form,"model":m._meta.verbose_name,
            "fields":fields})
    view_import.url=r"^import/(?P<model>[a-z1-9]+\.[a-z1-9]+)/$"
    view_import.url_name="import"
    view_import.access=HasPerm("import")
##
## Admin actions to export selected objectd as CSV
##
def admin_csv_export(modeladmin,request,queryset):
    return HttpResponse(csv_export(modeladmin.model,queryset),mimetype="text/csv; encoding=utf-8")
admin_csv_export.short_description="Export selected %(verbose_name_plural)s to CSV"
admin.site.add_action(admin_csv_export,"export_selected_csv")