# ---------------------------------------------------------------------
# Axis.VAPIX.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "Axis.VAPIX.get_local_users"
    interface = IGetLocalUsers

    axpairs = {"axadmin": "superuser", "axoper": "operator", "axview": "view"}

    def adduser(self, section, userclass):
        users = self.axconfig.get(section).split(",")
        for user in users:
            if user not in self.userlist:
                self.userlist += [user]
                self.r += [{"username": user, "class": userclass}]

    def execute(self):
        self.r = []
        self.userlist = []

        self.axconfig = self.profile.get_dict(
            self, command="/pwdgrp.cgi?action=get", eof_mark="logout"
        )

        for section, userclass in self.axpairs.items():
            self.adduser(section, userclass)

        return self.r
