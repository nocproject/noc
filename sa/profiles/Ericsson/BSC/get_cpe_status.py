# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cisco.IOS.get_interface_status
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcpe import IGetCPE


class Script(BaseScript):
    name = "Ericsson.BSC.get_cpe_status"
    interface = IGetCPE

    ALARM_MAP = {
        "MAINS ALARM": 101,
        "DOOR OPEN": 201,
        "OPEN DOOR": 202,
        "DOOR OPEN SYSTEM": 203,
        "DOOR OPEN (SYSTEM)": 204,
        "DOOR OPEN(SYS)": 205,
        "ENYTRANCE DOOR SYSTEM ALARM": 205,
        "FIER ALARM": 301,
        "FIRE ALARM": 302,
        "CONDITIONER ALARM": 401,
        "CONDICIONER ALARM": 402,
        "COND ALARM": 403,
        "HIGH TEMPERATUR ALARM": 501,
        "HIGH TEMPERATURE ALARM": 502,
        "HIGT TEMPERATURE ALARM": 503,
        "HIGH TEMPERATYRE ALARM": 504,
        "HIGH TEMPERATURE": 505,
        "HIGH TEMP": 506,
        "LOW TEMPERATURE": 601,
        "LOW TEMPERATURE ALARM": 602,
        "RECTIFIER ALARM": 701,
        "RECTIFIRE ALARM": 702,
        "LOW BATTERY": 801,
        "UNKNOWN": 9999
    }

    rx_alarm = re.compile(
        r"^(?P<alcls>\S+)\/(?P<alcat>\S+)\s+\"(?P<origin>\S+)\"\s(?P<alcurrno>\S+)\s+(?P<aldata>\S+)\s+(?P<altime>\S+)\s+"
        r":(?P<alfid>\S+),(?P<allevel>\S+),(?P<alnr>\S+);\s+"
        r"(?P<alarm>SYNCHRONOUS DIGITAL PATH FAULT SUPERVISION|"
        r"CELL LOGICAL CHANNEL AVAILABILITY SUPERVISION|DIGITAL PATH QUALITY SUPERVISION|CELL RF OUTPUT POWER SUPERVISION|"
        r"RADIO X-CEIVER ADMINISTRATION\nMANAGED OBJECT FAULT|RADIO X-CEIVER ADMINISTRATION REMOTE OMT OVER IP ENABLED|"
        r"RADIO X-CEIVER ADMINISTRATION\nBTS EXTERNAL FAULT|"
        r"BSC CAPACITY LOCK EXCEEDED|IO PRINTOUT DESTINATION FAULTY|CELL RESTRICTION ACTIVATED)\s+"
        r"(?P<alinfo>.+)",
        re.DOTALL | re.MULTILINE)

    def execute(self):
        result = []
        name = []
        aalarm = []
        ext = []
        moname = []
        with self.profile.mml(self):
            v = self.cli("ALLIP:DETAILS;")
            a = v.split("\n\n\n")
            for aa in a:
                match = self.rx_alarm.search(aa)
                if match:
                    alcls = match.group("alcls")
                    alcat = match.group("alcat")
                    if alcat != "EXT":
                        alfid = match.group("alfid")
                        alnr = match.group("alnr")
                        origin = match.group("origin")
                        bscname = origin.split("/")[0]
                        alcurrno = match.group("alcurrno")
                        aldata = match.group("aldata")
                        altime = match.group("altime")
                        alarm = match.group("alarm")
                        alinfo = match.group("alinfo")
                        f = alinfo.split("\n\n")
                        type = None
                        name = None
                        for i in self.profile.iter_items(f[0]):
                            if "MO" in i:
                                moname = i["MO"]
                                type = "bs"
                            if "RSITE" in i:
                                name = i["RSITE"]
                                type = "bs"
                            if "CELL" in i:
                                cell = i["CELL"]
                                type = "st"
                                cn = self.cli("RXTCP:MOTY=RXOTG,CELL=%s;" % cell)
                                for stn in self.profile.iter_items(cn):
                                    if "MO" in stn:
                                        name = stn["MO"] + "#" + stn["CELL"]
                                    else:
                                        name = cell
                            if "ALARM" in i and "SLOGAN" in i:
                                aalarm = i["ALARM"] + i["SLOGAN"]

                        r = {
                            "alcls": alcls,
                            "alarm": alarm,
                            "alfid": alfid,
                            "alnr": alnr,
                            "alcat": alcat,
                            "bscname": bscname,
                            "moname": moname,
                            "alcurrno": alcurrno,
                            "origin": origin,
                            "aldata": aldata,
                            "altime": altime,
                            "alinfo": alinfo,
                            "aalarm": aalarm,
                            "id": None,
                            "global_id": None,
                        }
                        if type:
                            r["type"] = type
                        else:
                            r["type"] = "other"
                        if name:
                            r["bsname"] = name
                        else:
                            r["bsname"] = bscname
                        result += [r]
                    else:
                        alinfo = match.group("alinfo")
                        f = alinfo.split("\n\n")
                        for i in self.profile.iter_items(f[0]):
                            if "MO" in i:
                                moname = i["MO"]
                                type = "bs"
                            if "RSITE" in i:
                                name = i["RSITE"]
                                type = "bs"
                        ex = [e.strip() for e in f[1].splitlines()]
                        ext = ex[1:]
                        for exte in ext:
                            if "MAINS ALARM" in exte:
                                exte = "MAINS ALARM"
                            if "DOOR OPEN" in exte:
                                exte = "DOOR OPEN"
                            if "LOW BATTERY" in exte:
                                exte = "LOW BATTERY"
                            try:
                                n = self.ALARM_MAP[exte]
                            except KeyError:
                                n = self.ALARM_MAP["UNKNOWN"]
                            exmoname = "%s#%s" % (moname, n)
                            external = exte
                            alfid = match.group("alfid")
                            alnr = match.group("alnr")
                            origin = match.group("origin")
                            bscname = origin.split("/")[0]
                            alcurrno = match.group("alcurrno")
                            aldata = match.group("aldata")
                            altime = match.group("altime")
                            alarm = match.group("alarm")
                            r = {
                                "alcls": alcls,
                                "alarm": alarm,
                                "alfid": alfid,
                                "alnr": alnr,
                                "alcat": alcat,
                                "bscname": bscname,
                                "bsname": name,
                                "extmoname": exmoname,
                                "moname": moname,
                                "extnumber": n,
                                "external": external,
                                "alcurrno": alcurrno,
                                "origin": origin,
                                "aldata": aldata,
                                "altime": altime,
                                "alinfo": alinfo,
                                "id": None,
                                "global_id": None,
                                "type": type
                            }
                            result += [r]
        return result
