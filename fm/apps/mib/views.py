# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIB Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## Django modules
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms.formsets import formset_factory
## NOC modules
from noc.lib.app import TreeApplication, HasPerm, view, PermitLogged
from noc.fm.models import MIB, MIBData, MIBRequiredException, SyntaxAlias
from noc.lib.fileutils import temporary_file
from noc.lib.validators import is_oid


class MIBApplication(TreeApplication):
    title = _("MIB")
    verbose_name = _("MIB")
    verbose_name_plural = _("MIBs")
    menu = "MIBs"
    model = MIB

    def get_syntax(self, x):
        def syntax_descr(syntax):
            if not syntax:
                return []
            s = []
            s += [syntax["base_type"]]
            if "display_hint" in syntax:
                s += ["display-hint: %s" % syntax["display_hint"]]
            if (syntax["base_type"] in ("Enumeration", "Bits") and
                "enum_map" in syntax):
                # Display enumeration
                for k in sorted(syntax["enum_map"],
                                key=lambda x: int(x)):
                    s += ["%s -> %s" % (k, syntax["enum_map"][k])]
            return s
        
        s = []
        sa = SyntaxAlias.rewrite(x.name, x.syntax)
        if x.syntax:
            s += syntax_descr(x.syntax)
        if sa != x.syntax:
            s += ["", "Effective syntax:"]
            s += syntax_descr(sa)
        return s
                
    def get_preview_extra(self, obj):
        """
        Collect additional data for preview
        """
        r = sorted(
            [
                {
                "oid": x.oid,
                "name": x.name,
                "description": x.description,
                "syntax": self.get_syntax(x),
                "aliases": x.aliases
            } for x in MIBData.objects.filter(mib=obj.id)] +
            [
                {
                "oid": x.oid,
                "name": x.name,
                "description": x.description,
                "syntax": self.get_syntax(x),
                "aliases": x.aliases
            } for x in MIBData.objects.filter(aliases__startswith=obj.name)],
            key=lambda x: [int(y) for y in x["oid"].split(".")])
        # Calculate indent
        min_l = 0
        for x in r:
            l = len(x["oid"].split("."))
            if min_l == 0 or l < min_l:
                min_l = l
            x["offset"] = l
        for x in r:
            x["offset"] -= min_l
            x["offset"] *= 16
        return {"data": r}

    @view(url="^go/(?P<go_type>[^/]+)/(?P<param>.+)/$",
          url_name="go", access=HasPerm("view"))
    def view_go(self, request, go_type, param):
        """
        Redirector
        """
        if go_type == "mib_name":
            mib = MIB.objects.filter(name=param).first()
            if mib:
                return self.response_redirect("fm:mib:preview", mib.id)
        return self.response_redirect("fm:mib.tree")

    @view(url="^lookup_mib/", url_name="lookup_mib", access=HasPerm("view"))
    def view_lookup_mib(self, request):
        """
        AJAX lookup of MIB
        """
        result = None
        if request.GET and "lookup_field" in request.GET:
            q = request.GET["lookup_field"].strip()
            if q:
                if "::" in q:
                    r = MIB.get_oid(q)
                    if r:
                        result = {
                            "oid": r,
                            "name": q
                        }
                else:
                    r = MIB.get_name(q)
                    if r:
                        result = {
                            "oid": q,
                            "name": r
                        }
        return self.render_json(result)

    class MIBUploadForm(forms.Form):
        file = forms.FileField()

    @view(url=r"^add/$", url_name="add", access=HasPerm("add"))
    def view_add(self, request):
        upload_formset = formset_factory(self.MIBUploadForm, extra=10)
        if request.method=="POST":
            formset = upload_formset(request.POST, request.FILES)
            if formset.is_valid():
                # Load MIBs
                left = {}  # Form -> error
                for form in formset:
                    if "file" in form.cleaned_data:
                        left[form] = None
                
                # Try to upload MIBs
                uploaded = set()
                while len(left) > 0:
                    n = len(left)
                    for form in left.keys():
                        # Try to upload MIB
                        with temporary_file(form.cleaned_data["file"].read()) as path:
                            try:
                                mib = MIB.load(path)
                                uploaded.add(mib.name)
                                del left[form]
                            except MIBRequiredException, x:
                                left[form] = "%s requires %s" % (x.mib,
                                                                 x.requires_mib)
                    nn = len(left)
                    if n == nn:
                        break
                    else:
                        n = nn
                # Check no unresolved dependencies left
                uploaded = ", ".join(sorted(uploaded))
                if uploaded:
                    self.message_user(request,
                        "Following MIBs are loaded correctly: %s" % uploaded)
                if left:
                    for form in left:
                        self.message_user(request,
                                          "%s load failed: %s" % (form.cleaned_data["file"].name, left[form]))
                return self.response_redirect(self.base_url)
        else:
            formset = upload_formset()
        return self.render(request, "add.html", form=formset)

    @view(url="help/(?P<key>\S+)/", url_name="help", access=PermitLogged())
    def view_help(self, request, key):
        # Get OID
        if "::" in key:
            oid = MIB.get_oid(key)
        elif is_oid(key):
            oid = key
        else:
            raise self.response_not_found("Key not found")
        # Find data
        l_oid = oid.split(".")
        data = None
        while l_oid:
            c_oid = ".".join(l_oid)
            d = MIBData.objects.filter(oid=c_oid).first()
            if d:
                data = d
                break
            l_oid.pop(-1)
        if data is None:
            raise self.response_not_found("No help available")
        return self.render(request, "help.html", data=data,
                           syntax=self.get_syntax(data))
