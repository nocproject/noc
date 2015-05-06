# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.mib application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models.mib import MIB
from noc.fm.models.mibdata import MIBData
from noc.fm.models.syntaxalias import SyntaxAlias
from noc.lib.fileutils import temporary_file


class MIBApplication(ExtDocApplication):
    """
    MIB application
    """
    title = "MIB"
    menu = "MIB"
    model = MIB

    @view(url="^(?P<id>[0-9a-f]{24})/data/$", method=["GET"],
          access="launch", api=True)
    def api_data(self, request, id):
        def insert_tree(data, ds):
            if (len(data["path"]) + 1 == len(ds["path"])
                and data["path"] == ds["path"][:-1]):
                # Direct child
                data["children"] = data.get("children", []) + [ds]
            else:
                if "children" not in data:
                    data["children"] = []
                # Descendant
                for c in data["children"]:
                    if c["path"] == ds["path"][:len(c["path"])]:
                        insert_tree(c, ds)
                        return
                cp = ds["path"][:-(len(data["path"]) + 1)]
                c = {
                    "oid": ".".join(str(x) for x in cp),
                    "path": cp,
                    "children": []
                }
                data["children"] += [c]
                insert_tree(c, ds)

        def fix_tree(data):
            if "path" in data:
                del data["path"]
            if "children" in data:
                if "leaf" in data:
                    del data["leaf"]
                data["children"] = sorted(data["children"],
                                          key=lambda x: x["path"])
                data["expanded"] = True
                for c in data["children"]:
                    fix_tree(c)

        mib = self.get_object_or_404(MIB, id=id)
        data = {
            "oid": "",
            "leaf": True,
            "path": []
        }
        for d in MIBData.objects.filter(mib=mib.id).order_by("oid"):
            ds = {
                "oid": d.oid,
                "name": d.name,
                "path": [int(x) for x in d.oid.split(".")],
                "leaf": True,
                "description": d.description,
                "syntax": self.get_syntax(d)
            }
            insert_tree(data, ds)
        fix_tree(data)
        return data

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
        return "\n".join(s)

    @view(url="^upload/", method=["POST"], access="create", api=True)
    def api_upload(self, request):
        left = {}  # name -> data
        for f in request.FILES:
            left[f] = request.FILES[f]
        errors = {}
        while len(left):
            n = len(left)
            for name in left.keys():
                with temporary_file(left[name].read()) as path:
                    try:
                        MIB.load(path)
                        del left[name]
                        if name in errors:
                            del errors[name]
                    except MIB.MIBRequiredException, x:
                        errors[name] = "%s requires MIBs %s" % (
                            x.mib, x.requires_mib)
            if len(left) == n:
                # Failed to upload anything, stopping
                break
        r = {
            "success": len(left) == 0,
            "errors": errors
        }
        return r

    @view(url="^(?P<id>[0-9a-f]{24})/text/$", method=["GET"],
          access="launch", api=True)
    def api_text(self, request, id):
        mib = self.get_object_or_404(MIB, id=id)
        return mib.get_text()
