# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Dahua.DH.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "Dahua.DH.get_local_users"
    interface = IGetLocalUsers

    def execute(self):
        r = {}
        users_info = self.http.get("/cgi-bin/userManager.cgi?action=getUserInfoAll")
        for line, value in self.profile.parse_tokens(users_info):
            line_id = line[1]
            if line_id not in r:
                r[line_id] = {}
            if line[2] in {"Id", "Name", "Group"}:
                if line[2] == "Name":
                    r[line_id]["username"] = value
                elif line[2] == "Group":
                    r[line_id]["class"] = value
        return list(six.itervalues(r))
