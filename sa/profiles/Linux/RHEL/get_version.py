# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linux.RHEL.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion

class Script(BaseScript):
    name = "Linux.RHEL.get_version"
    cache = True
    interface = IGetVersion

    """
    Fedora release 23 (Twenty Three)
    CentOS release 5.11 (Final)
    CentOS release 6.7 (Final)
    CentOS Linux release 7.2.1511 (Core) 
    Red Hat Enterprise Linux Server release 6.6 (Santiago)
    """ 

    rx_ver = re.compile(
        r"(?P<distr>[^,]+) release (?P<version>[^ ,]+) \((?P<codename>[^,]+)\)"
        , re.MULTILINE | re.DOTALL | re.IGNORECASE)

    """
    http://unix.stackexchange.com/questions/89714/easy-way-to-determine-virtualization-technology
    """
    check_virtual_xen = re.compile(r"(?P<virtplatform>\S+) virtual console successfully installed as",
                                   re.MULTILINE | re.DOTALL | re.IGNORECASE)
    check_virtual_vmware = re.compile(r"VMware.*\s+Vendor:\s(?P<virtplatform>\S+)",
                                      re.MULTILINE | re.DOTALL | re.IGNORECASE)
    check_virtual_kvm = re.compile(r".*Booting paravirtualized kernel on (?P<virtplatform>\S+)\n",
                                   re.MULTILINE | re.DOTALL | re.IGNORECASE)
    check_virtual_dom0 = re.compile(r"Booting paravirtualized kernel on (?P<virtplatform>\S+) hardware\n",
                                    re.MULTILINE | re.DOTALL | re.IGNORECASE)
    check_virtual_qemu = re.compile(r": \S+ (?P<virtplatform>\S+) Virtual CPU version \S+ stepping \d+",
                                    re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def execute(self):

        version = None
        codename = ""
        distr = ""

        r = self.cli("cat /etc/redhat-release", cached=True)
        if "No such file or directory" not in r:
            match = self.re_search(self.rx_ver, r)
            version = match.group("version")
            codename = match.group("codename")
            distr = match.group("distr")

        plat = self.cli("uname -p", cached=True)
        kernel = self.cli("uname -r")

        """
        see http://www.dmo.ca/blog/detecting-virtualization-on-linux/
        """
        virtual = None
        virtual = str(self.cli("dmesg | grep -i -E \"(U Virtual|on KVM|Xen virtual c)\";"))

        if virtual and not virtual.startswith('dmesg'):
            rx = self.find_re([
                self.check_virtual_kvm,
                self.check_virtual_vmware,
                self.check_virtual_xen,
                self.check_virtual_dom0,
                self.check_virtual_qemu
                ], virtual)

            match1 = rx.search(virtual)
        
            if match1.group("virtplatform") == "bare":
                # print (match1.group("virtplatform"))
                virtualplatform = ""
            else:
                virtualplatform = match1.group("virtplatform")
                # print (virtualplatform)
                virtualplatform = "".join((" ", virtualplatform))
        else:
            print ("HUI")
            virtualplatform = ""

        return {
            "vendor": "Red Hat",
            "platform": "".join((plat.strip(), virtualplatform)),
            "version": version,
            "attributes": {
                "codename": codename,
                "distro": distr,
                "kernel": kernel.strip(),
                }
            }
