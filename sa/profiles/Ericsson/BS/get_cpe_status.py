# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cisco.IOS.get_interface_status
# ----------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE


class Script(BaseScript):
    name = "Ericsson.BS.get_cpe_status"
    interface = IGetCPE

    def execute(self):
        result = []
        alfid, alcls, alnr, altime, alinfo, alarm, sp, moi, moc = None, None, None, None, None, None, None, None, None
        with self.profile.ncli(self):
            v = self.cli("alarms")
            a = v.split("\n\n")
            for aa in a:
                if "ALARM DATA" in aa:
                    aa = aa.replace("ALARM DATA\n", "")
                    for line in aa.splitlines():
                        r = line.split("=", 1)
                        if r[0].strip() == "Alarm Id":
                            alfid = r[1].strip()
                        if r[0].strip() == "Probable Cause":
                            alarm = r[1].strip()
                        if r[0].strip() == "Probable Cause Code":
                            alnr = r[1].strip()
                        if r[0].strip() == "Event Time":
                            altime = r[1].strip()
                        if r[0].strip() == "Perceived Severity":
                            alcls = r[1].strip()
                        if r[0].strip() == "Specific Problem":
                            sp = r[1].strip()
                        if r[0].strip() == "Managed Object Class":
                            moc = r[1].strip()
                        if r[0].strip() == "Managed Object Instance":
                            moi = r[1].strip()
                        if r[0].strip() == "Additional Text":
                            alinfo = r[1].strip()
                            result += [{
                                "alcls": alcls,
                                "alarm": alarm,
                                "alfid": alfid,
                                "alnr": alnr,
                                "altime": altime,
                                "alinfo": alinfo,
                                "sp": sp,
                                "moc": moc,
                                "moi": moi,
                                "type": "bs",
                                "id": None,
                                "global_id": None
                            }]
        return result
