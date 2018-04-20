# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CSV Export/Import application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.db import transaction
## Django modules
from django.db import models
## NOC modules
from noc.lib.app import Application, view
from noc.lib.csvutils import csv_export, csv_import, get_model_fields,\
    IR_FAIL, IR_SKIP, IR_UPDATE


class CSVApplication(Application):
    title = "CSV Export/Import"

    @view(url="^$", url_name="index", menu="Setup | CSV Export/Import",
        access="import")
    def view_index(self, request):
        class ModelForm(forms.Form):
            model = forms.ChoiceField(
                choices=[
                    (m._meta.db_table.replace("_", "."),
                     m._meta.db_table.replace("_", "."))
                    for m in sorted(models.get_models(),
                    key=lambda x: x._meta.db_table)])
            action = forms.CharField(widget=forms.HiddenInput)

        if request.POST:
            form = ModelForm(request.POST)
            if form.is_valid():
                if form.cleaned_data["action"] == "Export":
                    app, m = form.cleaned_data["model"].split(".", 1)
                    model = models.get_model(app, m)
                    if not model:
                        return self.response_not_found("Invalid model")
                    return self.render_plain_text(
                        csv_export(model),
                        mimetype="text/csv; encoding=utf-8"
                    )
                else:
                    return self.response_redirect("main:csv:import",
                        form.cleaned_data["model"])
        else:
            form = ModelForm()
        return self.render(request,
            "index.html", form=form)

    class ImportForm(forms.Form):
        """
        CSV import form
        """
        file = forms.FileField()
        resolve = forms.ChoiceField(choices=[
            (IR_FAIL, "Fail"),
            (IR_SKIP, "Skip"),
            (IR_UPDATE, "Update")
        ])
        referer = forms.CharField(widget=forms.HiddenInput)

    @view(url=r"^import/(?P<model>[a-z1-9]+\.[a-z1-9]+)/$",
          url_name="import", access="import")
    def view_import(self, request, model):
        """
        Import from CSV file
        :param request:
        :param model:
        :return:
        """
        a, m = model.split(".")
        m = get_object_or_404(ContentType, app_label=a, model=m).model_class()
        if request.POST:
            form = self.ImportForm(request.POST, request.FILES)
            if form.is_valid():
                count, error = csv_import(m, request.FILES["file"],
                                        resolution=form.cleaned_data["resolve"])
                if error:
                    # Rollback current transaction to be able to send message
                    transaction.rollback()
                if count is None:
                    self.message_user(request,
                                      "Error importing data: %s" % error)
                else:
                    self.message_user(request,
                                      "%d records are imported/updated" % count)
                return self.response_redirect(form.cleaned_data["referer"])
        else:
            form = self.ImportForm(
                    {"referer": request.META.get("HTTP_REFERER", "/")})
        # Prepare fields description
        fields = []
        for name, required, rel, rname in get_model_fields(m):
            if rel:
                db_table = rel._meta.db_table
                r = ["%s.\"id\"" % db_table]
                if rname != "id":
                    r = ["%s.\"%s\"" % (db_table, rname)] + r
            else:
                r = []
            fields += [(name, required, " or ".join(r))]
        return self.render(request, "import.html",
                           form=form, model=m._meta.verbose_name, fields=fields)


##
## Admin actions to export selected objects as CSV
##
def admin_csv_export(modeladmin, request, queryset):
    return HttpResponse(csv_export(modeladmin.model, queryset),
                        mimetype="text/csv; encoding=utf-8")

admin_csv_export.short_description = "Export selected %(verbose_name_plural)s to CSV"
admin.site.add_action(admin_csv_export, "export_selected_csv")
