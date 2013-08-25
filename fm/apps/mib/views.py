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
                "leaf": True
            }
            insert_tree(data, ds)
        fix_tree(data)
        return data