# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# network-scan command
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import asyncio
import datetime
from io import BytesIO
import logging
import socket

# Third-party modules
import xlsxwriter
from gufo.ping import Ping

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.validators import is_ipv4
from noc.core.ip import IP
from noc.core.ioloop.snmp import snmp_get, SNMPError
from noc.core.mib import mib
from noc.core.snmp.version import SNMP_v1, SNMP_v2c
from noc.sa.models.managedobject import ManagedObject, ManagedObjectProfile
from noc.sa.models.credentialcheckrule import CredentialCheckRule
from noc.sa.models.managedobject import AdministrativeDomain
from noc.inv.models.networksegment import NetworkSegment
from noc.main.models.pool import Pool
from noc.sa.models.profile import Profile
from noc.inv.models.platform import Platform
from noc.services.mailsender.service import MailSenderService
from noc.main.models.notificationgroup import NotificationGroup
from noc.core.comp import smart_text
from noc.core.mongo.connection import connect
from noc.config import config


# example
# ./noc network-scan 10.0.0.0/24
# ./noc network-scan --autoadd test --email example@example.org --formats xlsx 10.0.0.0/24
# ./noc network-scan --in /opt/net/nets --exclude /opt/net/exclude


class Command(BaseCommand):
    DEFAULT_OID = "1.3.6.1.2.1.1.2.0"
    DEFAULT_COMMUNITY = "public"
    CHECK_OIDS = [mib["SNMPv2-MIB::sysObjectID.0"], mib["SNMPv2-MIB::sysName.0"]]
    CHECK_VERSION = {SNMP_v1: "snmp_v2c_get", SNMP_v2c: "snmp_v1_get"}
    SNMP_VERSION = {0: "SNMP_v1", 1: "SNMP_v2c"}

    def add_arguments(self, parser):
        parser.add_argument("--in", action="append", dest="inputs", help="File with addresses")
        parser.add_argument(
            "--import", action="append", dest="imports", help="File to import into NOC"
        )
        parser.add_argument(
            "--exclude", action="append", dest="exclude", help="File with addresses for exclusion"
        )
        parser.add_argument(
            "--jobs", action="store", type=int, default=100, dest="jobs", help="Concurrent jobs"
        )
        parser.add_argument("addresses", nargs=argparse.REMAINDER, help="Object name")
        parser.add_argument("--community", action="append", help="SNMP community")
        parser.add_argument("--oid", default=self.CHECK_OIDS, action="append", help="SNMP GET OIDs")
        parser.add_argument("--timeout", type=int, default=1, help="SNMP GET timeout")
        parser.add_argument("--version", type=int, help="version snmp check")
        parser.add_argument("--obj-profile", help="name object profile", default="default")
        parser.add_argument("--credential", help="credential profile")
        parser.add_argument("--pool", help="name pool", default="default")
        parser.add_argument("--adm-domain", help="name adm domain", default="default")
        parser.add_argument("--segment", help="network segment", default="ALL")
        parser.add_argument("--label", action="append", help="mo label")
        parser.add_argument("--autoadd", help="add object", action="store_true")
        parser.add_argument("--syslog-source", choices=["m", "a"], help="syslog_source")
        parser.add_argument("--trap-source", choices=["m", "a"], help="trap_source")
        parser.add_argument("--mail", help="mail notification_group name")
        parser.add_argument("--email", action="append", help="mailbox list")
        parser.add_argument("--formats", default="csv", help="Format file (csv or xlsx)")
        parser.add_argument("--resolve-name-snmp", action="store_true", help="hostname->name")
        parser.add_argument("--resolve-name-dns", action="store_true", help="ptr dns->name")

    def handle(
        self,
        inputs,
        imports,
        exclude,
        addresses,
        jobs,
        community,
        oid,
        timeout,
        version,
        credential,
        pool,
        adm_domain,
        segment,
        obj_profile,
        autoadd,
        label,
        mail,
        email,
        formats,
        resolve_name_snmp,
        resolve_name_dns,
        syslog_source,
        trap_source,
        *args,
        **options,
    ):
        async def ping_task():
            queue = asyncio.Queue(maxsize=self.jobs)
            for _ in range(self.jobs):
                asyncio.create_task(self.ping_worker(queue))
            # Read exclude addresses from files
            """
            file example
            10.0.0.1
            10.1.1.0/24
            10.1.2.1
            """
            if exclude:
                for fn in exclude:
                    try:
                        with open(fn) as f:
                            for line in f:
                                line = line.strip()
                                ip = line.split("/")
                                if is_ipv4(ip[0]):
                                    if len(ip) == 2:
                                        ip = IP.prefix(line)
                                        first = ip.first
                                        last = ip.last
                                        for x in first.iter_address(until=last):
                                            ip2 = str(x).split("/")
                                            self.hosts_exclude.add(ip2[0])
                                    else:
                                        self.hosts_exclude.add(line)
                    except OSError as e:
                        self.die("Cannot read file %s: %s\n" % (fn, e))
            # Direct addresses 10.0.0.1 or 10.0.0.0/24
            for a in addresses:
                self.addresses = set()
                self.nets.append(a)
                ip = a.split("/")
                if not is_ipv4(ip[0]):
                    continue
                if len(ip) == 2:
                    ip = IP.prefix(a)
                    first = ip.first
                    last = ip.last
                    for x in first.iter_address(until=last):
                        ip2 = str(x).split("/")
                        if ip2[0] not in self.hosts_exclude:
                            await queue.put(ip2[0])
                elif a not in self.hosts_exclude:
                    await queue.put(a)

            # Read addresses from files
            """
            file example
            10.0.0.1
            10.1.1.0/24
            10.1.2.1
            """
            if inputs:
                for fn in inputs:
                    try:
                        with open(fn) as f:
                            for line in f:
                                line = line.strip()
                                ip = line.split("/")
                                if is_ipv4(ip[0]):
                                    self.nets.append(line)
                                    if len(ip) == 2:
                                        ip = IP.prefix(line)
                                        first = ip.first
                                        last = ip.last
                                        for x in first.iter_address(until=last):
                                            ip2 = str(x).split("/")
                                            if ip2[0] not in self.hosts_exclude:
                                                await queue.put(ip2[0])
                                    elif line not in self.hosts_exclude:
                                        await queue.put(line)

                    except OSError as e:
                        self.die("Cannot read file %s: %s\n" % (fn, e))
            await queue.join()

        async def snmp_task():
            queue = asyncio.Queue(maxsize=self.jobs)
            for _ in range(self.jobs):
                asyncio.create_task(self.snmp_worker(queue, community, oid, timeout, self.version))
            for a in self.enable_ping:
                await queue.put(a)
            await queue.join()

        connect()
        self.addresses = set()  # ip for ping
        self.enable_ping = set()  # ip ping
        self.not_ping = set()  # ip not ping
        self.enable_snmp = set()  # ip responding snmp
        self.hosts_enable = set()  # ip in noc
        self.hosts_exclude = set()  # ip exclude
        self.mo = {}
        self.snmp = {}
        self.nets = []  # nets
        self.count_ping = 0
        self.count_not_ping = 0
        self.count_snmp = 0
        self.count_net = 0

        # options by-default
        # administrative_domain = "default"
        profile = "Generic.Host"
        # object_profile = "default"
        description = "create object %s" % (datetime.datetime.now().strftime("%Y%m%d"))
        # segment = "ALL"
        # scheme = "1"
        # address = ""
        # port = ""
        # user=""
        # password=""
        # super_password = ""
        # remote_path = ""
        # trap_source_ip = ""
        # trap_community = ""
        # snmp_ro=""
        # snmp_rw=""
        # vc_domain = "default"
        # vrf = ""
        # termination_group = ""
        # service_terminator = ""
        # shape = "Cisco/router"
        # config_filter_rule = ""
        # config_diff_filter_rule = ""
        # config_validation_rule = ""
        # max_scripts = "1"
        # labels = ["autoadd"]
        # pool = "default"
        # container = ""
        # trap_source_type = "d"
        # syslog_source_type = "d"
        # object_profile="default"
        # time_pattern = ""
        # x = ""
        # y = ""
        # default_zoom = ""

        # key processing
        if version is None:
            self.version = [1, 0]
        else:
            self.version = [version]
        try:
            self.pool = Pool.objects.get(name=pool)
        except Pool.DoesNotExist:
            self.die("Invalid pool-%s" % pool)
        # snmp community
        if not community:
            community = []
            if credential:
                try:
                    self.cred = CredentialCheckRule.objects.get(name=credential)
                except CredentialCheckRule.DoesNotExist:
                    self.die("Invalid credential profile-%s" % credential)
                for snmp in self.cred.suggest_snmp:
                    community.append(snmp.snmp_ro)
            else:
                community = [self.DEFAULT_COMMUNITY]

        # auto add objects profile
        if autoadd:
            try:
                self.adm_domain = AdministrativeDomain.objects.get(name=adm_domain)
            except AdministrativeDomain.DoesNotExist:
                self.die("Invalid adm profile-%s")
            self.profile = Profile.objects.get(name=profile)
            try:
                self.segment = NetworkSegment.objects.get(name=segment)
            except NetworkSegment.DoesNotExist:
                self.die("Invalid network segment-%s")
            try:
                self.object_profile = ManagedObjectProfile.objects.get(name=obj_profile)
            except ManagedObjectProfile.DoesNotExist:
                self.die("Invalid object profile-%s")

        # creating a list of presence mo in noc
        moall = ManagedObject.objects.filter(is_managed=True)
        moall = moall.filter(pool=self.pool)
        for mm in moall:
            self.hosts_enable.add(mm.address)
            self.mo[mm.address] = {
                "name": mm.name,
                "labels": mm.labels,
                "is_managed": mm.is_managed,
                "snmp_ro": mm.auth_profile.snmp_ro if mm.auth_profile else mm.snmp_ro,
            }
        # add to mo list with remote:deleted
        moall = ManagedObject.objects.filter(is_managed=False).exclude(
            labels__contains=["remote:deleted"]
        )
        moall = moall.filter(pool=self.pool)
        for mm in moall:
            if mm.address not in self.hosts_enable:
                self.hosts_enable.add(mm.address)
                self.mo[mm.address] = {
                    "name": mm.name,
                    "labels": mm.labels,
                    "is_managed": mm.is_managed,
                    "snmp_ro": mm.auth_profile.snmp_ro if mm.auth_profile else mm.snmp_ro,
                }
        # Ping
        self.ping = Ping(tos=config.ping.tos)
        self.jobs = jobs
        asyncio.run(ping_task())
        print("ver.16")
        print("enable_ping ", len(self.enable_ping))
        # snmp
        asyncio.run(snmp_task())
        print("enable_snmp ", len(self.enable_snmp))

        data = "IP;Available via ICMP;IP enable;is_managed;suggest name;SMNP sysname;SNMP sysObjectId;Vendor;Model;Name;pool;labels\n"
        for ipx in self.enable_ping:
            x2 = "True"
            x12 = ipx
            if resolve_name_dns:
                if self.get_domain_name(ipx):
                    x12 = self.get_domain_name(ipx)
            if resolve_name_snmp:
                if ipx in self.enable_snmp and "1.3.6.1.2.1.1.5.0" in self.snmp[ipx]:
                    x12 = self.snmp[ipx]["1.3.6.1.2.1.1.5.0"]
            x4 = x5 = x6 = x7 = x8 = x9 = x11 = "None"
            x12 = x12.strip()
            if ipx in self.hosts_enable:
                x3 = "True"
                x8 = self.mo[ipx]["name"]
                x11 = str(self.mo[ipx]["is_managed"])
                if self.mo[ipx]["labels"]:
                    x9 = ",".join(self.mo[ipx]["labels"] if self.mo[ipx]["labels"] else [])
            else:
                if autoadd:
                    m = ManagedObject(
                        name=x12 if not x12 or x12 != "" else ipx,
                        administrative_domain=self.adm_domain,
                        profile=self.profile,
                        description=description,
                        object_profile=self.object_profile,
                        segment=self.segment,
                        scheme=1,
                        address=ipx,
                        pool=self.pool,
                    )
                    if label:
                        m.labels = label
                    if syslog_source:
                        m.syslog_source_type = syslog_source
                    if trap_source:
                        m.trap_source_type = trap_source
                    try:
                        m.save()
                    except Exception as e:
                        print(e)
                x3 = "False"
            if ipx in self.enable_snmp:
                # ['1.3.6.1.2.1.1.2.0', '1.3.6.1.2.1.1.5.0']
                if "1.3.6.1.2.1.1.2.0" in self.snmp[ipx]:
                    x5 = self.snmp[ipx]["1.3.6.1.2.1.1.2.0"]
                    for p in Platform.objects.filter(snmp_sysobjectid=x5):
                        if p:
                            x6 = p.vendor
                            x7 = p.name
                else:
                    x5 = "None"

                if "1.3.6.1.2.1.1.5.0" in self.snmp[ipx]:
                    sysname = self.snmp[ipx]["1.3.6.1.2.1.1.5.0"]
                    x4 = sysname
                else:
                    x4 = "None"
                    # try:
                    #    sysname = self.snmp[ipx]["1.3.6.1.2.1.1.5.0"]
                    #    x4 = sysname
                    # except:
                    #    x4 = "None"
            s = ";".join(
                [
                    smart_text(ipx),
                    smart_text(x2),
                    smart_text(x3),
                    smart_text(x11),
                    smart_text(x12),
                    smart_text(x4),
                    smart_text(x5),
                    smart_text(x6),
                    smart_text(x7),
                    smart_text(x8),
                    smart_text(pool),
                    smart_text(x9),
                ]
            )
            data += s + "\n"

        fn = "/tmp/report.csv"
        file = open(fn, "w")
        file.write(data)
        file.close()
        # mail in notification_group
        if mail:
            if not email:
                email = []
            g = NotificationGroup.get_by_name(mail)
            for method, params, lang in g.active_members:
                if "mail" in method:
                    email.append(params)

        # output in csv or mail
        if email:
            bodymessage = "Report in attachment.\n\nscan network:\n"
            for adr in self.nets:
                bodymessage += adr + "\n"
            filename = "found_ip_%s" % (datetime.datetime.now().strftime("%Y%m%d"))
            if formats == "csv":
                f = "%s.csv" % filename
                attach = [{"filename": f, "data": data}]
            elif formats == "xlsx":
                f = "%s.xlsx" % filename
                response = BytesIO()
                wb = xlsxwriter.Workbook(response)
                ws = wb.add_worksheet("Objects")
                row = 0
                ss = data.split("\n")
                for line in ss:
                    row_data = str(line).strip("\n")
                    rr = row_data.split(";")
                    ws.write_row(row, 0, tuple(rr))
                    # Move on to the next worksheet row.
                    row += 1
                wb.close()
                response.seek(0)
                attach = [
                    {"filename": f, "data": response.getvalue(), "transfer-encoding": "base64"}
                ]
                response.close()
            ms = MailSenderService()
            ms.logger = logging.getLogger("network_scan")
            self.i = 1
            for boxmail in email:
                self.i += 1
                msg = {
                    "address": boxmail,
                    "subject": "Report (%s)" % pool,
                    "body": bodymessage,
                    "attachments": attach,
                }
                ms.send_mail(self.i, msg)
            """
            msg = {
                "address": email,
                "subject": "Report (%s)" % pool,
                "body": bodymessage,
                "attachments": attach,
            }
            ms.send_mail("11", msg)
            """
        else:
            print(data)

    async def ping_check(self, addr: str) -> bool:
        """
        Try to ping address.

        Args:
            addr: Address to ping.

        Returns:
            * True, on success.
            * False, otherwise.
        """
        for _ in range(3):  # @todo: Make configurable
            rtt = await self.ping.ping(addr)
            if rtt is not None:
                return True
        return False

    async def ping_worker(self, queue):
        while True:
            a = await queue.get()
            if a and await self.ping_check(a):
                self.enable_ping.add(a)
            queue.task_done()
            if not a:
                break

    async def snmp_worker(self, queue, community, oid, timeout, version):
        while True:
            a = await queue.get()
            if not a:
                queue.task_done()
                break
            if a in self.hosts_enable:
                community = [self.mo[a]["snmp_ro"]]
            if not community[0] is None:
                for c in community:
                    for ver in version:
                        try:
                            self.r = await snmp_get(
                                address=a,
                                oids=dict((k, k) for k in oid),
                                community=c,
                                version=ver,
                                timeout=timeout,
                            )
                            # self.s = "OK"
                            self.enable_snmp.add(a)
                            self.snmp[a] = self.r
                            self.snmp[a]["version"] = ver
                            self.snmp[a]["community"] = c
                            break
                        except SNMPError as e:
                            # self.s = "FAIL"
                            self.r = str(e)
                        except Exception as e:
                            # self.s = "EXCEPTION"
                            self.r = str(e)
                            break
            queue.task_done()

    @staticmethod
    def get_domain_name(ip_address):
        try:
            result = socket.gethostbyaddr(ip_address)
        except Exception:
            return
        return list(result)[0]


if __name__ == "__main__":
    Command().run()
