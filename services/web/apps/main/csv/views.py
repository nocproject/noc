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
# Modules for parsing CSV
import csv
import StringIO


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
                        "/main/csv/%s/" % form.cleaned_data["model"]
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

    def address_in_network(self, ip, net):
        """Is an address in a network"""
        ipaddr = int(''.join(['%02x' % int(x) for x in ip.split('.')]), 16)
        netstr, bits = net.split('/')
        netaddr = int(''.join(['%02x' % int(x) for x in netstr.split('.')]), 16)
        mask = (0xffffffff << (32 - int(bits))) & 0xffffffff
        return (ipaddr & mask) == (netaddr & mask)

    @view(url=r"^import/(?P<model>[a-zA-Z1-9]+\.[a-zA-Z1-9]+)/$",
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

            def import_check_perms():
                accepted_row = []
                forbidden_row = []
                if get_model_id(m) == 'ip.Address':
                    accepted_prefixes = get_model('ip.PrefixAccess').objects.filter(user=request.user,
                                                                                    can_change=True).values_list(
                        'prefix', 'vrf_id')
                    csv_reader = csv.DictReader(request.FILES['file'])
                    keys = None
                    for row in csv_reader:
                        if not keys:
                            keys = row.keys()
                        for prefix in accepted_prefixes:
                            if self.address_in_network(row['address'], prefix[0])\
                                    and get_model('ip.VRF').objects.get(id=prefix[1]).name == row['vrf']:
                                accepted_row.append(row)
                                if row['address'] in forbidden_row:
                                    forbidden_row.remove(row['address'])
                            else:
                                forbidden_row.append(row['address'])
                    forbidden_ip = list(set(forbidden_row))

                    new_csv_file = StringIO.StringIO()
                    dict_writer = csv.DictWriter(new_csv_file, keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(accepted_row)
                    check_msg = ", \n\nskipped because of PrefixAccess - %d IP: \n%s" % (len(forbidden_ip), "\n".join(forbidden_ip))
                else:
                    new_csv_file = request.FILES["file"]
                    check_msg = ""
                return new_csv_file, check_msg

            if form.is_valid():
                if request.user.is_superuser:
                    csv_file = request.FILES["file"]
                    resp_msg = ""
                else:
                    csv_file, resp_msg = import_check_perms()
                count, error = csv_import(
                    m, csv_file,
                    resolution=form.cleaned_data["resolve"]
                )
                if count is None:
                    self.message_user(request,
                                      "Error importing data: %s" % error)
                else:
                    return HttpResponse("%d records are imported/updated" % count + resp_msg, content_type="text/plain")
                    # self.message_user(request, "%d records are imported/updated" % count + resp_msg)
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
