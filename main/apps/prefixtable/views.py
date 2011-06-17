# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PrefixTable Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
from django import forms
## NOC modiles
from noc.lib.app import ModelApplication, view, HasPerm
from noc.main.models import PrefixTable, PrefixTablePrefix
from noc.lib.validators import is_ipv4, is_ipv6, is_ipv4_prefix, is_ipv6_prefix
from noc.lib.ip import IP
##
## Prefixes inline form
##
class PrefixTableInlineForm(forms.ModelForm):
    class Meta:
        model = PrefixTablePrefix
    
##
## Prefixes inline
##
class PrefixTableInline(admin.TabularInline):
    form = PrefixTableInlineForm
    model = PrefixTablePrefix
    extra = 3
    exclude = ["afi"]

##
## PrefixTable admin
##
class PrefixTableAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name", "description"]
    inlines = [PrefixTableInline]
    actions = ["test_prefix_tables"]
    
    def test_prefix_tables(self, request, queryset):
        return self.app.response_redirect("main:prefixtable:test",
                                     ",".join([str(p.id) for p in queryset]))
    test_prefix_tables.short_description="Test selected Prefix Tables"

##
## PrefixTable application
##
class PrefixTableApplication(ModelApplication):
    model = PrefixTable
    model_admin = PrefixTableAdmin
    menu = "Setup | Prefix Tables"
    
    class PTForm(forms.Form):
        prefix = forms.CharField()
        
        def clean_prefix(self):
            p = self.cleaned_data["prefix"]
            for v in [is_ipv4, is_ipv6, is_ipv4_prefix, is_ipv6_prefix]:
                if v(p):
                    return IP.prefix(p).prefix
            raise forms.ValidationError("Invalid Prefix")
        
    
    @view(url=r"test/(?P<ids>\S+)/$", url_name="test",
          access=HasPerm("change"))
    def view_test(self, request, ids):
        pts = [self.get_object_or_404(PrefixTable, id=int(x))
               for x in ids.split(",")]
        r = []
        if request.POST:
            form = self.PTForm(request.POST)
            if form.is_valid():
                prefix = form.cleaned_data["prefix"]
                r = [(p, p.match(prefix)) for p in pts]
        else:
            form = self.PTForm()
        return self.render(request, "test.html", form=form, result=r)
    
