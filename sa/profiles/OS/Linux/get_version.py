# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.Linux.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "OS.Linux.get_version"
    cache = True
    implements = [IGetVersion]

    rx_distrib = re.compile(r"^DISTRIB_ID=+(?P<distrib>\S+)$", re.MULTILINE)
    rx_release = re.compile(
        r"^DISTRIB_RELEASE=+(?P<release>\S+)$", re.MULTILINE)
    rx_vendor = re.compile(
        r"option 'Manufacturer' '(?P<vendor>\S+)'$", re.MULTILINE)
    rx_platform = re.compile(
        r"option 'ProductClass' '(?P<platform>\S+)'$", re.MULTILINE)
    rx_platform_board = re.compile(
        r"^board.name=+(?P<platform>.+)$", re.MULTILINE)
    rx_platform_proc = re.compile(
        r"^cpu model+\s+:+\s+(?P<platform>.+)$", re.MULTILINE)
    rx_version = re.compile(
        r"option 'SoftwareVersion' '(?P<version>\S+)'$", re.MULTILINE)
    rx_ubnt_version = re.compile(r"\.v(?P<version>[^@]+)@")
    rx_eltex_version = re.compile(
        r"^Eltex\/(?P<platform>\S+)\s+Version\s+(?P<version>\S+)\s")
    rx_proc = re.compile(r"BOARD Name\s+:+\t+(?P<version>.+)")
    rx_hardware = re.compile(
        r"option 'HardwareVersion' '(?P<hardware>\S+)'$", re.MULTILINE)
    rx_serial = re.compile(
        r"option 'SerialNumber' '(?P<serial>\S+)'$", re.MULTILINE)
    rx_grub = re.compile(r"^grub \(+(?P<boot>.+)+\)$", re.MULTILINE)

    def execute(self):
        vendor = ''
        platform = ''
        version = ''
        cmd = "cat /etc/config/general 2>/dev/null; echo 2>/dev/null"
        general = self.cli(cmd)
        gen = general.split('\n')
        if len(gen) > 3:
            ven = self.re_search(self.rx_vendor, general)
            if ven:
                vendor = ven.group("vendor")
            plat = self.re_search(self.rx_platform, general)
            if plat:
                platform = plat.group("platform")
            ver = self.re_search(self.rx_version, general)
            if ver:
                version = ver.group("version")
            hard = self.re_search(self.rx_hardware, general)
            if hard:
                hardware = hard.group("hardware")
            ser = self.re_search(self.rx_serial, general)
            if ser:
                serial = ser.group("serial")

        if not platform:
            cmd = "cat /etc/board.info 2>/dev/null"
            plat = self.rx_platform_board.search(self.cli(cmd))
            if plat:
                platform = plat.group("platform")
                if 'NanoStation' in platform or 'PowerStation' in platform or \
                        'AirGrid' in platform or 'NanoBridge' in platform or\
                        'PowerBridge' in platform or 'Rocket' in platform or\
                        'Bullet' in platform:
                    vendor = 'Ubiquity'
                    # Replace # with @ to prevent prompt matching
                    ps1 = self.cli("echo $PS1|sed 's/#/@/'")
                    match = self.rx_ubnt_version.search(ps1)
                    version = match.group("version")
        if not platform:
            plat = self.cli("uname -m 2>/dev/null")
            if plat:
                platform = plat.split('\n')[0]
        if not platform:
            plat = self.cli("cat /proc/cpuinfo 2>/dev/null")
            match = self.rx_proc.search(plat)
            if match:
                s = match.group("version")
                if s.count('-') == 2:
                    s = s.split('-')
                    vendor = s[0]
                    if vendor == 'ELTEX':
                        vendor = 'Eltex'
                    platform = s[1]
                    version = s[2]
                else:
                    platform = s
        if not platform:
            match = self.rx_platform_proc.search(plat)
            if match:
                platform = match.group("platform")
        if not platform:
            platform = "Unknown"

# TODO better...
        if platform == 'MIPS 4Kc V0.10':
            el = self.cli("ls /flash/ 2>/dev/null")
            if 'tau' in el:
                vendor = 'Eltex'
                platform = 'TAU-1'

        if not vendor or not version:
            cmd = "cat /etc/*{-,_}{release,version} 2>/dev/null; echo ''"
            vers = self.cli(cmd)
            ver = vers.split('\n')
            if len(ver) > 3:
                distrib = self.re_search(self.rx_distrib, vers)
                release = self.re_search(self.rx_release, vers)
                if distrib:
                    vendor = distrib.group("distrib")
                if release:
                    version = release.group("release")
            if not version:
                version = ver[0]

        if not vendor:
            ven = self.cli("uname -s 2>/dev/null")
            ven = ven.split('\n')[0]
            if ven:
                vendor = "GNU/" + ven
            else:
                vendor = "Unknown"

        if not version:
# Russian latter!!!
#            vers = self.cli(smart_str("cat /etc/version 2>/dev/null"))
#            match = self.rx_eltex_version.search(vers)
#            if match:
#                vendor = 'Eltex'
#                platform = match.group("platform")
#                version = match.group("version")
            version = vers.split('\n')[0]
        if not version:
            vers = self.cli("uname -r 2>/dev/null")
            version = vers.split('\n')[0]
        if not version:
            version = "Unknown"

        bver = self.cli("grub --version 2>/dev/null")
        if bver:
            bver = self.re_search(self.rx_grub, bver)
            if bver:
                boot = bver.group("boot")

        r = {"vendor": vendor,
            "platform": platform,
            "version": version,
            "attributes": {
                }
            }

        try:
            if boot:
                r["attributes"].update({"Boot PROM": boot})
        except NameError:
            pass
        try:
            if hardware:
                r["attributes"].update({"HW version": hardware})
        except NameError:
            pass
        try:
            if serial:
                r["attributes"].update({"Serial Number": serial})
        except NameError:
            pass
        return r
