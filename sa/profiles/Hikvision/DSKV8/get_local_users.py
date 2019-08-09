# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Hikvision.DSKV8.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import xml.etree.ElementTree as ElementTree
from copy import copy

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "Hikvision.DSKV8.get_local_users"
    interface = IGetLocalUsers

    def xml_2_dict(self, r, root=True):
        if root:
            t = r.tag.split("}")[1][0:]
            return {t: self.xml_2_dict(r, False)}
        d = copy(r.attrib)
        if r.text:
            d["_text"] = r.text
        for x in r.findall("./*"):
            t = x.tag.split("}")[1][0:]
            if t not in d:
                d[t] = []
            d[t].append(self.xml_2_dict(x, False))
        return d

    def execute(self):
        r = []
        v = self.http.get("/ISAPI/Security/users", json=False, cached=True, use_basic=True)
        root = ElementTree.fromstring(v)
        v = self.xml_2_dict(root)
        users = v["UserList"]["User"]

        for i in users:
            r += [
                {
                    "username": i["userName"][0]["_text"],
                    "class": {
                        "Administrator": "superuser",
                        "Viewer": "operator",
                        "Operator": "operator",
                    }[i["userLevel"][0]["_text"]],
                    "is_active": True,
                }
            ]
        return r
