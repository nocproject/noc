# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Huawei.U2000.get_cpe_status
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE


class Script(BaseScript):
    name = "Huawei.U2000.get_cpe_status"
    interface = IGetCPE

    rx_alarm = re.compile(r"ALARM\s+(?P<alarmid>\d+)\s+Fault\s+(?P<alarmtype>\S+)\s+"
                          r"\S+\s+(?P<bscid>\d+)\s+(?P<alarmname>\S+)\s+"
                          r"Sync serial No.\s+=\s+(?P<syncser>\d+)\s+"
                          r"Alarm\sname\s+=\s+(?P<alarmsp>\S.+)\s+"
                          r"Alarm\sraised\stime\s+=\s+(?P<alarmtime>\S.+)\s+"
                          r"Location\sinfo\s+=\s+(?P<localinfo>[\S\s]+)", re.MULTILINE)

    rx_index = re.compile(
        r"Site\s+No.=(?P<siteindex>\d+),\s+\S.+(\s+|\s+\S+|\s+\S.*),\s+Site\s+Name=(?P<sitename>\S.*)", re.MULTILINE)
    rx_index_cell = re.compile(r"Site\s+Index=(?P<siteindex>\S+),\s+Cell\s+Index(?P<cellindex>\S+),"
                               r"[\S\s]+Site\s+Name=(?P<sitename>\S.*),\sCell\s+Name=(?P<cellname>\S+),", re.MULTILINE)

    rx_alarm_lte = re.compile(r"ALARM\s+(?P<alarmid>\d+)\s+Fault\s+(?P<alarmtype>\S+)\s+"
                              r"\S+\s+(?P<bscid>\d+)\s+(?P<alarmname>\S+)\s+"
                              r"Sync\sserial\sNo.\s+=\s+(?P<syncser>\d+)\s+"
                              r"Alarm\sname\s+=\s+(?P<alarmsp>\S.*)\s+"
                              r"Alarm\sraised\stime\s+=\s+(?P<alarmtime>\S.*)\s+"
                              r"Location\sinfo\s+=\s+(?P<localinfo>\S.*|)\s+(?:Alarm changed time|Common alarm)",
                              re.MULTILINE)

    def execute(self):
        result = []
        cmd = self.mml("LST NEBYOMC")
        v = cmd.split("\r\n\r\n")[2]
        for line in v.splitlines():
            tp = line.split("   ")[0].strip()
            name = line.split("   ")[1].strip()
            ip = line.split("   ")[2].strip()
            if "BSC" in tp:
                with self.profile.mml_ne(self, ip):
                    bts = self.mml("LST ALMAF:SRC=ALL;")
                    for r in bts.split("\r\n\r\n"):
                        for match in self.rx_alarm.finditer(r):
                            alfid = match.group("alarmid").strip()
                            alnr = match.group("syncser").strip()
                            alcls = match.group("alarmtype").strip()
                            sp = match.group("alarmsp").strip()
                            alarm = match.group("alarmname").upper().strip()
                            altime = match.group("alarmtime").strip()
                            alinfo = match.group("localinfo").strip()
                            if "cell" in alinfo.lower():
                                for cell_index in self.rx_index_cell.finditer(alinfo):
                                    sitename = cell_index.group("sitename").strip()
                                    cellname = cell_index.group("cellname").strip()
                                    res = {
                                        "alcls": alcls.upper(),
                                        "alarm": alarm,
                                        "bsname": "%s#%s" % (sitename, cellname),
                                        "alfid": "%s.%s" % (name, alfid),
                                        "alnr": alnr,
                                        "altime": altime,
                                        "alinfo": alinfo,
                                        "sp": sp,
                                        "moc": name,
                                        "moi": "%s.%s" % (sitename, cellname),
                                        "type": "st",
                                        "id": None,
                                        "global_id": None
                                    }
                                    result += [res]
                            else:
                                for index in self.rx_index.finditer(alinfo):
                                    moindex = index.group("siteindex").strip()
                                    moname = index.group("sitename").strip()
                                    res = {
                                        "alcls": alcls.upper(),
                                        "alarm": alarm,
                                        "bsname": moname,
                                        "alfid": "%s.%s" % (name, alfid),
                                        "alnr": alnr,
                                        "altime": altime,
                                        "alinfo": alinfo,
                                        "sp": sp,
                                        "moc": name,
                                        "moi": moindex,
                                        "type": "bs",
                                        "id": None,
                                        "global_id": None
                                    }
                                    result += [res]

            elif "BTS" in tp or "BNE" in tp:
                with self.profile.mml_ne(self, ip) as ne:
                    if ne == "NE does not Connection" or ne == "Unknown exception":
                        continue
                    bts = self.mml("LST ALMAF:;")
                    if bts == "No record exists":
                        continue
                    for r in bts.split("\r\n\r\n"):
                        for match in self.rx_alarm_lte.finditer(r):
                            alfid = match.group("alarmid").strip()
                            alnr = match.group("syncser").strip()
                            alcls = match.group("alarmtype").strip()
                            sp = match.group("alarmsp").strip()
                            alarm = match.group("alarmname").upper().strip()
                            altime = match.group("alarmtime").strip()
                            alinfo = match.group("localinfo").strip()
                            res = {
                                "alcls": alcls.upper(),
                                "alarm": alarm,
                                "bsname": name,
                                "alfid": "%s.%s" % (name, alfid),
                                "alnr": alnr,
                                "altime": altime,
                                "alinfo": alinfo,
                                "sp": sp,
                                "moc": name,
                                "moi": "".join(i for i in ip.split(".")),
                                "type": "bs",
                                "id": None,
                                "global_id": None
                            }
                            result += [res]
            else:
                continue

        return result
