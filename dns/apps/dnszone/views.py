# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNSZone Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
from django import forms
from django.contrib import admin
from django.utils.safestring import SafeString
## NOC modules
from noc.lib.app import ModelApplication, HasPerm, view
from noc.dns.models import DNSZone, DNSZoneRecord, DNSServer, DNSZoneProfile
from noc.main.models import Schedule
from noc.lib.validators import is_fqdn
from noc.lib.app.site import site

##
## Distribution list
## @todo: use alias
##
def distribution(obj):
    return ", ".join(
            [u"<a href='%s'>%s</a>" % (
            site.reverse("dns:dnszone:view_zone", obj.id, n.id),
            n.name)
            for n in obj.distribution_list])
distribution.short_description = "Distribution"
distribution.allow_tags = True

##
## Override auto-generated column
##
def ag(obj):
    return "<img src='/media/img/admin/icon-%s.gif'>" % {True: "yes",
                                            False: "no"}[obj.is_auto_generated]
ag.short_description = SafeString("Auto<br/>Gen.")
ag.allow_tags = True

##
## Validation form for RR inlines
##
class DNSZoneRecordInlineForm(forms.ModelForm):
    class Meta:
        model = DNSZoneRecord
    def clean_right(self):
        s = []
        if "left" in self.cleaned_data:
            s += [self.cleaned_data["left"]]
        s += [self.cleaned_data["type"].type]
        if "right" in self.cleaned_data:
            s += [self.cleaned_data["right"]]
        s = " ".join(s)
        if not self.cleaned_data["type"].is_valid(s):
            raise forms.ValidationError("Invalid record")
        return self.cleaned_data["right"]
##
## RR inline form
##
class DNSZoneRecordInline(admin.TabularInline):
    form = DNSZoneRecordInlineForm
    model = DNSZoneRecord
    extra = 3
##
## DNSZone admin
##
class DNSZoneAdmin(admin.ModelAdmin):
    inlines = [DNSZoneRecordInline]
    list_display = ["name", "description", "paid_till", ag,
                    "profile", "serial", distribution, "notification_group"]
    list_filter = ["is_auto_generated", "profile"]
    search_fields = ["name", "description"]
    actions = ["rpsl_for_selected"]
    ##
    ## Generate RPSL for selected objects
    ##
    def rpsl_for_selected(self, request, queryset):
        s = "\n\n".join([o.rpsl for o in queryset])
        return self.app.render_plain_text(s)
    rpsl_for_selected.short_description = "RPSL for selected objects"
##
## DNSZone application
##
class DNSZoneApplication(ModelApplication):
    model = DNSZone
    model_admin = DNSZoneAdmin
    menu = "Zones"
    ##
    ## Render zone content
    ##
    @view(url=r"^(?P<zone_id>\d+)/ns/(?P<ns_id>\d+)/$",
          url_name="view_zone", access=HasPerm("change"))
    def view_zone(self, request, zone_id, ns_id):
        z = self.get_object_or_404(DNSZone, id=int(zone_id))
        ns = self.get_object_or_404(DNSServer, id=int(ns_id))
        return self.render_plain_text(z.zonedata(ns))
    
    ##
    ## Zone upload form
    ##
    class ZonesUploadForm(ModelApplication.Form):
        profile = forms.ModelChoiceField(label="Zone Profile",
            queryset=DNSZoneProfile.objects)
        file = forms.FileField(label="File")
    ##
    ## Render tools page
    ##
    @view(url=r"^tools/$", url_name="tools", access=HasPerm("tools"))
    def view_tools(self, request):
        return self.render(request, "tools.html",
                           {"zones_upload_form": self.ZonesUploadForm()})
    
    ##
    ## Upload zones
    ##
    @view(url=r"^tools/upload/$", url_name="upload", access=HasPerm("tools"))
    def view_upload(self, request):
        if request.POST and request.FILES:
            form = self.ZonesUploadForm(request.POST, request.FILES)
            if form.is_valid():
                profile = form.cleaned_data["profile"]
                n = 0
                # Create missed records
                for l in request.FILES["file"].read().split("\n"):
                    l = l.strip().lower()
                    if not l or not is_fqdn(l):
                        continue
                    try:
                        DNSZone.objects.get(name=l)
                        continue  # Skip existing zones
                    except DNSZone.DoesNotExist:
                        pass
                    DNSZone(name=l, is_auto_generated=False,
                            profile=profile).save()
                    n += 1
                if n == 0:
                    self.message_user(request, "No new zones found")
                else:
                    # Trigger dns.update_domain_expiration to update paid_till
                    Schedule.reschedule("dns.update_domain_expiration",
                        minutes=10)
                    self.message_user(request, "%d new zones are imported" % n)
                return self.response_redirect(self.base_url)
            else:
                # Render tools
                return self.render(request, "tools.html",
                                   {"zones_upload_form": form})
        return self.response_redirect("dns:dnszone:tools")
    
