# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# CSV Export/Import application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django import forms
from django.contrib import admin
from django.db import models
from django.http import HttpResponse
from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.application import Application, view
from noc.core.csvutils import csv_export, csv_import, get_model_fields, IR_FAIL, IR_SKIP, IR_UPDATE
from noc.models import get_model, get_model_id


class CSVApplication(Application):
    title = _("CSV Export/Import")

    @view(url="^$", url_name="index",
          menu=[_("Setup"), _("CSV Export/Import")],
          access="import")
    def view_index(self, request):
        class ModelForm(forms.Form):
            model = forms.ChoiceField(
                choices=[
                    (get_model_id(m), get_model_id(m))
                    for m in sorted(
                        models.get_models(),
                        key=lambda x: x._meta.db_table)
                ]
            )
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
                    return self.response_redirect(
                        "main:csv:import",
                        form.cleaned_data["model"]
                    )
        else:
            form = ModelForm()
        return self.render(request, "index.html", form=form)

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
        m = get_model(model)
        if not m:
            return self.response_not_found("Invalid model")
        if request.POST:
            form = self.ImportForm(request.POST, request.FILES)
            if form.is_valid():
                count, error = csv_import(
                    m, request.FILES["file"],
                    resolution=form.cleaned_data["resolve"]
                )
                if count is None:
                    self.message_user(request,
                                      "Error importing data: %s" % error)
                else:
                    self.message_user(request,
                                      "%d records are imported/updated" % count)
                return self.response_redirect(form.cleaned_data["referer"])
        else:
            form = self.ImportForm({
                "referer": request.META.get("HTTP_REFERER", "/")
            })
        # Prepare fields description
        fields = []
        for name, required, rel, rname in get_model_fields(m):
            if rel:
                if isinstance(rel._meta, dict):
                    r = ["%s.%s" % (rel._meta["collection"], rname)]
                else:
                    db_table = rel._meta.db_table
                    r = ["%s.\"id\"" % db_table]
                    if rname != "id":
                        r = ["%s.\"%s\"" % (db_table, rname)] + r
            else:
                r = []
            fields += [(name, required, " or ".join(r))]
        return self.render(request, "import.html",
                           form=form, model=m._meta.verbose_name, fields=fields)


#
# Admin actions to export selected objects as CSV
#
def admin_csv_export(modeladmin, request, queryset):
    return HttpResponse(csv_export(modeladmin.model, queryset),
                        mimetype="text/csv; encoding=utf-8")


admin_csv_export.short_description = "Export selected %(verbose_name_plural)s to CSV"
admin.site.add_action(admin_csv_export, "export_selected_csv")
