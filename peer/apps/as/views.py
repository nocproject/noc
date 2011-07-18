# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AS Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication, site
from noc.peer.models import AS
from noc.ip.models import Prefix


def allocated_prefixes(obj):
    if obj.asn == 0:
        return ""
    r = []
    for p in Prefix.objects.filter(asn=obj).order_by("afi", "prefix"):
        r += ["<a href='%s'>%s</a>" % (site.reverse("ip:ipam:vrf_index",
                                                    p.vrf.id, p.afi, p.prefix),
                                       p.prefix)]
    return ", ".join(r)
allocated_prefixes.short_description = "Prefixes"
allocated_prefixes.allow_tags = True


class ASAdmin(admin.ModelAdmin):
    """
    AS Admin
    """
    list_display = ["asn", "as_name", "description", "organisation",
                    allocated_prefixes]
    search_fields = ["asn", "description"]
    filter_horizontal = ["administrative_contacts", "tech_contacts",
                         "maintainers", "routes_maintainers"]
    actions = ["rpsl_for_selected", "update_rir_db_for_selected"]

    def rpsl_for_selected(self, request, queryset):
        """
        Generate RPSL for selected objects
        """
        return self.app.render_plain_text("\n\n".join([o.rpsl
                                                       for o in queryset]))
    rpsl_for_selected.short_description = "RPSL for selected objects"

    def update_rir_db_for_selected(self, request, queryset):
        """
        Update RIR's database for selected object
        """
        u = request.user
        if not u or not u.is_superuser:
            self.message_user(request, "Superuser priveleges required")
            return
        r = []
        for a in queryset:
            r += ["AS%s %s:\n" % (a.asn, a.as_name) + a.update_rir_db()]
        return self.app.render_plain_text("\n\n".join(r))
    update_rir_db_for_selected.short_description = "Update RIR DB for selected objects"


class ASApplication(ModelApplication):
    """
    AS application
    """
    model = AS
    model_admin = ASAdmin
    menu = "ASes"
