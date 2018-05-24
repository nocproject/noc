# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# MAC Checkfff
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import datetime
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.alarmescalation import AlarmEscalation
from noc.fm.models.utils import get_alarm


class CPESTATUSCheck(DiscoveryCheck):
    """
    CPE status/alarm discovery
    """
    name = "cpes"
    # required_capabilities = ["Mobile | BSC"]
    required_script = "get_cpe_status"

    SEV_MAP = {
        "A1": 5000,
        "A2": 5000,
        "A3": 2000,
        "O1": 3000,
        "O2": 3000
    }

    def handler(self):
        if self.object.profile.name == "Ericsson.BSC":
            self.ericsson_bsc()
        if self.object.profile.name == "Ericsson.BS":
            self.ericsson_bs()
        if self.object.profile.name == "Huawei.U2000":
            self.huawei_u2000()

    def ericsson_bsc(self):
        self.logger.info("Checking Alarm CPEs")
        co_id = self.object.id  # controller id
        result = self.object.scripts.get_cpe_status()  # result get_cpe_status
        # System Alarms
        aptalarms = {str(a.vars["alfid"]): a for a in
                     ActiveAlarm.objects.filter(vars__bscid=co_id, vars__alcat__contains="AP",
                                                vars__alfid__exists=True)}
        extalarms = {str(a.vars["extmoname"]): a for a in
                     ActiveAlarm.objects.filter(vars__bscid=co_id, vars__alcat="EXT", vars__alfid__exists=True)}
        # Controller Alarms
        bscaptalarm = {str(cpe["alfid"]): cpe for cpe in result if "AP" in cpe["alcat"]}
        bscextalarm = {str(cpe["extmoname"]): cpe for cpe in result if cpe["alcat"] == "EXT"}
        # Check if System Alarm = Controller Alarms
        lockapt = set(aptalarms.keys()).intersection(set(bscaptalarm))
        if lockapt:
            self.logger.info("Check BSC vs System OK")
        lockext = set(extalarms.keys()).intersection(set(bscextalarm))
        if lockext:
            self.logger.info("Check BSC vs System OK")
        # Search bscalarm in alarm, if bscalarm not in alarm, create!
        addalarmapt = set(bscaptalarm.keys()) - set(aptalarms.keys())
        for aa in addalarmapt:
            # Check bscname, if not bscname. Create alarm fo bs and sector
            if bscaptalarm[aa]["bsname"] != self.object.name:
                mo = self.find_cpe(bscaptalarm[aa]["bsname"], co_id)
                if mo:
                    alarmclass = AlarmClass.objects.get(
                        name="BSC | PM | %s" % bscaptalarm[aa]["alarm"].replace("\n", " "))
                    alarm = ActiveAlarm(
                        timestamp=datetime.datetime.now(),
                        managed_object=mo.id,
                        alarm_class=alarmclass,
                        severity=self.SEV_MAP[bscaptalarm[aa]["alcls"]],
                        vars={
                            "alcls": bscaptalarm[aa]["alcls"],
                            "bscalarm": bscaptalarm[aa]["alarm"],
                            "alfid": bscaptalarm[aa]["alfid"],
                            "alnr": bscaptalarm[aa]["alnr"],
                            "alcat": bscaptalarm[aa]["alcat"],
                            "origin": bscaptalarm[aa]["origin"],
                            "objectname": bscaptalarm[aa]["bsname"],
                            "alcurrno": bscaptalarm[aa]["alcurrno"],
                            "aldata": bscaptalarm[aa]["aldata"],
                            "altime": bscaptalarm[aa]["altime"],
                            "alinfo": bscaptalarm[aa]["alinfo"],
                            "moname": bscaptalarm[aa]["moname"],
                            "bscid": co_id
                        }
                    )
                    alarm.save()
                    self.logger.info("Raising alarm %s %s with severity %s",
                                     alarmclass.name, alarm.id, alarm.severity)
                    # print alarm.id
                    ealarm = get_alarm(alarm.id)
                    AlarmEscalation.watch_escalations(ealarm)
                    self.logger.info("Start watch escalation for Alarm %s",
                                     alarmclass.name)
            # Else create alarm for Controller
            else:
                alarmclass = AlarmClass.objects.get(name="BSC | PM | %s" % bscaptalarm[aa]["alarm"].replace("\n", " "))
                alarm = ActiveAlarm(
                    timestamp=datetime.datetime.now(),
                    managed_object=self.object.id,
                    alarm_class=alarmclass,
                    severity=self.SEV_MAP[bscaptalarm[aa]["alcls"]],
                    vars={
                        "objectname": self.object.name,
                        "alcls": bscaptalarm[aa]["alcls"],
                        "bscalarm": bscaptalarm[aa]["alarm"],
                        "alfid": bscaptalarm[aa]["alfid"],
                        "alnr": bscaptalarm[aa]["alnr"],
                        "alcat": bscaptalarm[aa]["alcat"],
                        "origin": bscaptalarm[aa]["origin"],
                        "alcurrno": bscaptalarm[aa]["alcurrno"],
                        "aldata": bscaptalarm[aa]["aldata"],
                        "altime": bscaptalarm[aa]["altime"],
                        "alinfo": bscaptalarm[aa]["alinfo"],
                        "moname": bscaptalarm[aa]["moname"],
                        "bscid": co_id
                    }
                )
                alarm.save()
                self.logger.info("Raising alarm %s %s with severity %s",
                                 alarmclass.name, alarm.id, alarm.severity)
                # print alarm.id
                ealarm = get_alarm(alarm.id)
                AlarmEscalation.watch_escalations(ealarm)
                self.logger.info("Start watch escalation for Alarm %s",
                                 alarmclass.name)
        # Search alarm in bscalarm, if alarm not in bscalarm, close!
        closealarmapt = set(aptalarms.keys()) - set(bscaptalarm.keys())
        for ca in closealarmapt:
            al = aptalarms[ca]
            if al:
                # Clear alarm
                self.logger.info("Alarm are OK. Clearing alarm %s", al)
                al.clear_alarm("Alarm are OK")
            else:
                pass
        addalarmext = set(bscextalarm.keys()) - set(extalarms.keys())
        for ea in addalarmext:
            if bscextalarm[ea]["extnumber"] > 100 and bscextalarm[ea]["extnumber"] < 199:
                external = "MAINS ALARM"
            elif bscextalarm[ea]["extnumber"] > 200 and bscextalarm[ea]["extnumber"] < 299:
                external = "DOOR OPEN"
            elif bscextalarm[ea]["extnumber"] > 300 and bscextalarm[ea]["extnumber"] < 399:
                external = "FIRE ALARM"
            elif bscextalarm[ea]["extnumber"] > 400 and bscextalarm[ea]["extnumber"] < 499:
                external = "CONDITIONER ALARM"
            elif bscextalarm[ea]["extnumber"] > 500 and bscextalarm[ea]["extnumber"] < 599:
                external = "HIGH TEMPERATURE ALARM"
            elif bscextalarm[ea]["extnumber"] > 600 and bscextalarm[ea]["extnumber"] < 699:
                external = "LOW TEMPERATURE ALARM"
            elif bscextalarm[ea]["extnumber"] > 700 and bscextalarm[ea]["extnumber"] < 799:
                external = "RECTIFIER ALARM"
            elif bscextalarm[ea]["extnumber"] > 800 and bscextalarm[ea]["extnumber"] < 899:
                external = "LOW BATTERY ALARM"
            elif bscextalarm[ea]["extnumber"] == 9999:
                external = "UNKNOWN"
            else:
                external = "UNKNOWN"
            # Check bscname, if not bscname. Create alarm fo bs and sector
            mo = self.find_cpe(bscextalarm[ea]["bsname"], co_id)
            if mo:
                alarmclass = AlarmClass.objects.get(
                    name="BSC | PM | %s | %s" % (bscextalarm[ea]["alarm"].replace("\n", " "), external))
                # Check bscname, if not bscname. Create alarm fo bs and sector
                alarm = ActiveAlarm.objects.filter(managed_object=mo.id, alarm_class=alarmclass).first()
                if alarm:
                    self.logger.debug("Alarm OK")
                    continue
                else:
                    alarm = ActiveAlarm(
                        timestamp=datetime.datetime.now(),
                        managed_object=mo.id,
                        alarm_class=alarmclass,
                        severity=self.SEV_MAP[bscextalarm[ea]["alcls"]],
                        vars={
                            "alcls": bscextalarm[ea]["alcls"],
                            "bscalarm": bscextalarm[ea]["alarm"],
                            "alfid": bscextalarm[ea]["alfid"],
                            "alnr": bscextalarm[ea]["alnr"],
                            "alcat": bscextalarm[ea]["alcat"],
                            "origin": bscextalarm[ea]["origin"],
                            "objectname": bscextalarm[ea]["bsname"],
                            "alcurrno": bscextalarm[ea]["alcurrno"],
                            "aldata": bscextalarm[ea]["aldata"],
                            "altime": bscextalarm[ea]["altime"],
                            "alinfo": bscextalarm[ea]["alinfo"],
                            "moname": bscextalarm[ea]["moname"],
                            "external": bscextalarm[ea]["external"],
                            "extnumber": bscextalarm[ea]["extnumber"],
                            "extmoname": bscextalarm[ea]["extmoname"],
                            "bscid": co_id
                        }
                    )
                    alarm.save()
                    self.logger.info("Raising alarm %s %s with severity %s",
                                     alarmclass.name, alarm.id, alarm.severity)
                    # print alarm.id
                    ealarm = get_alarm(alarm.id)
                    AlarmEscalation.watch_escalations(ealarm)
                    self.logger.info("Start watch escalation for Alarm %s", alarmclass.name)

        # Search alarm in bscalarm, if alarm not in bscalarm, close!
        closealarmext = set(extalarms.keys()) - set(bscextalarm.keys())
        for ca in closealarmext:
            al = extalarms[ca]
            if al:
                # Clear alarm
                self.logger.info("Alarm are OK. Clearing alarm %s", al)
                al.clear_alarm("Alarm are OK")
            else:
                pass

    def ericsson_bs(self):
        self.logger.info("Checking Alarm BS")
        co_id = self.object.id  # controller id
        result = self.object.scripts.get_cpe_status()  # result get_cpe_status
        # System Alarms
        aptalarms = {str(a.vars["alfid"]): a for a in
                     ActiveAlarm.objects.filter(managed_object=co_id, vars__alfid__exists=True)}
        # print aptalarms.keys()
        # Controller Alarms
        bscaptalarm = {str(cpe["alfid"]): cpe for cpe in result}
        # print bscaptalarm.keys()
        # Check if System Alarm = Controller Alarms
        lockapt = set(aptalarms.keys()).intersection(set(bscaptalarm))
        if lockapt:
            self.logger.debug("OK")
        # Search bscalarm in alarm, if bscalarm not in alarm, create!
        addalarmapt = set(bscaptalarm.keys()) - set(aptalarms.keys())
        for aa in addalarmapt:
            # Check bscname, if not bscname. Create alarm fo bs and sector
            alarmclass = AlarmClass.objects.filter(name="BS | PM | %s" % bscaptalarm[aa]["alarm"]).first()
            if not alarmclass:
                alarmclass = AlarmClass.objects.get(name="BS | PM | UNKNOWN")
            alarm = ActiveAlarm(
                timestamp=datetime.datetime.now(),
                managed_object=self.object.id,
                alarm_class=alarmclass,
                severity=alarmclass.default_severity.severity,
                vars={
                    "alcls": bscaptalarm[aa]["alcls"],
                    "bscalarm": bscaptalarm[aa]["alarm"],
                    "alfid": bscaptalarm[aa]["alfid"],
                    "alnr": bscaptalarm[aa]["alnr"],
                    "altime": bscaptalarm[aa]["altime"],
                    "alinfo": bscaptalarm[aa]["alinfo"],
                    "sp": bscaptalarm[aa]["sp"],
                    "moi": bscaptalarm[aa]["moi"],
                    "moc": bscaptalarm[aa]["moc"]
                }
            )
            alarm.save()
            self.logger.info("Raising alarm %s %s with severity %s",
                             alarmclass.name, alarm.id, alarm.severity)
            # print alarm.id
            # ealarm = get_alarm(alarm.id)
            # AlarmEscalation.watch_escalations(ealarm)
            # self.logger.info("Start watch escalation for Alarm %s",
            #                 alarmclass.name)
        # Search alarm in bscalarm, if alarm not in bscalarm, close!
        closealarmapt = set(aptalarms.keys()) - set(bscaptalarm.keys())
        for ca in closealarmapt:
            al = aptalarms[ca]
            if al:
                # Clear alarm
                self.logger.info("Alarm are OK. Clearing alarm %s", al)
                al.clear_alarm("Alarm are OK")
            else:
                pass

    def huawei_u2000(self):
        self.logger.info("Checking Alarm BS")
        co_id = self.object.id  # controller id
        result = self.object.scripts.get_cpe_status()  # result get_cpe_status
        # System Alarms
        aptalarms = {str(a.vars["alfid"]): a for a in
                     ActiveAlarm.objects.filter(vars__bscid=co_id,
                                                vars__alfid__exists=True)}
        # print (aptalarms.keys())
        # Controller Alarms
        bscaptalarm = {str(cpe["alfid"]): cpe for cpe in result}
        # print (bscaptalarm.keys())
        # Check if System Alarm = Controller Alarms
        lockapt = set(aptalarms.keys()).intersection(set(bscaptalarm))
        if lockapt:
            self.logger.debug("OK")
        # Search bscalarm in alarm, if bscalarm not in alarm, create!
        addalarmapt = set(bscaptalarm.keys()) - set(aptalarms.keys())
        for aa in addalarmapt:
            # Check bscname, if not bscname. Create alarm fo bs and sector
            if bscaptalarm[aa]["bsname"] != self.object.name:
                mo = self.find_cpe(bscaptalarm[aa]["bsname"], co_id)
                if mo:
                    # Check bscname, if not bscname. Create alarm fo bs and sector
                    severity = AlarmSeverity.objects.filter(name=bscaptalarm[aa]["alcls"]).first()
                    if not severity:
                        severity = AlarmSeverity.objects.get(name="INFO")
                    alarmclass = AlarmClass.objects.filter(name="BS | PM | %s" % bscaptalarm[aa]["alarm"]).first()
                    if not alarmclass:
                        alarmclass = AlarmClass.objects.get(name="BS | PM | UNKNOWN")
                    alarm = ActiveAlarm(
                        timestamp=datetime.datetime.now(),
                        managed_object=mo.id,
                        alarm_class=alarmclass,
                        severity=severity.severity,
                        vars={
                            "alcls": bscaptalarm[aa]["alcls"],
                            "bscalarm": bscaptalarm[aa]["alarm"],
                            "alfid": bscaptalarm[aa]["alfid"],
                            "alnr": bscaptalarm[aa]["alnr"],
                            "altime": bscaptalarm[aa]["altime"],
                            "alinfo": bscaptalarm[aa]["alinfo"],
                            "sp": bscaptalarm[aa]["sp"],
                            "moi": bscaptalarm[aa]["moi"],
                            "moc": bscaptalarm[aa]["moc"],
                            "bscid": co_id
                        }
                    )
                    alarm.save()
                    self.logger.info("Raising alarm %s %s for %s with severity %s",
                                     alarmclass.name, alarm.id, mo.name, alarm.severity)
                    # print alarm.id
                    # ealarm = get_alarm(alarm.id)
                    # AlarmEscalation.watch_escalations(ealarm)
                    # self.logger.info("Start watch escalation for Alarm %s",
                    #                 alarmclass.name)

                else:
                    self.logger.info("No MO %s", bscaptalarm[aa]["bsname"])
        # Search alarm in bscalarm, if alarm not in bscalarm, close!
        closealarmapt = set(aptalarms.keys()) - set(bscaptalarm.keys())
        for ca in closealarmapt:
            al = aptalarms[ca]
            if al:
                # Clear alarm
                self.logger.info("Alarm are OK. Clearing alarm %s", al)
                al.clear_alarm("Alarm are OK")
            else:
                pass

    @classmethod
    def find_cpe(cls, bsname, co_id):
        try:
            return ManagedObject.objects.get(name=bsname, controller=co_id)
        except ManagedObject.DoesNotExist:
            return None
