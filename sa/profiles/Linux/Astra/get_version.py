# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linux.Astra.get_version
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
    name = "Linux.Astra.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(r"(?P<distr>\S+)\s+(?P<version>\S+)\s+\((?P<codename>\S+)\)$", re.MULTILINE)

    """
    http://unix.stackexchange.com/questions/89714/easy-way-to-determine-virtualization-technology
    """
    check_virtual_xen = re.compile(
        r"(?P<virtplatform>\S+) virtual console successfully installed as", re.MULTILINE
    )
    check_virtual_vmware = re.compile(r"VMware.*Platform/(?P<virtplatform>.*),", re.MULTILINE)
    check_virtual_kvm = re.compile(
        r".*Booting paravirtualized kernel on (?P<virtplatform>\S+)\n", re.MULTILINE
    )
    check_virtual_dom0 = re.compile(
        r"Booting paravirtualized kernel on (?P<virtplatform>\S+) (hypervisor|hardware)\n",
        re.MULTILINE,
    )
    check_virtual_qemu = re.compile(
        r": \S+ (?P<virtplatform>\S+) Virtual CPU version \S+ stepping \d+", re.MULTILINE
    )

    def execute_cli(self):

        version = None
        codename = ""
        distr = ""

        r = self.cli("cat /etc/astra_version", cached=True)
        if "No such file or directory" not in r:
            match = self.rx_ver.search(r)
            version = match.group("version")
            codename = match.group("codename")
            distr = match.group("distr")

        plat = self.cli("uname -p")
        kernel = self.cli("uname -r")

        """
        see http://www.dmo.ca/blog/detecting-virtualization-on-linux/
        """
        virtual = None
        virtual = str(self.cli('dmesg | grep -i -E "(Virtual|on KVM|Xen virtual c)"'))

        if virtual:
            rx = self.find_re(
                [
                    self.check_virtual_kvm,
                    self.check_virtual_vmware,
                    self.check_virtual_xen,
                    self.check_virtual_dom0,
                    self.check_virtual_qemu,
                ],
                virtual,
            )
            match1 = rx.search(virtual)

            if match1.group("virtplatform") == "bare":
                # print (match1.group("virtplatform"))
                virtualplatform = ""
            else:
                virtualplatform = match1.group("virtplatform")
                # print (virtualplatform)
                virtualplatform = "".join((" ", virtualplatform))
        else:
            virtualplatform = ""

        return {
            "vendor": "Astra",
            "platform": "".join((plat.strip(), virtualplatform)),
            "version": version,
            "attributes": {"codename": codename, "distro": distr, "kernel": kernel.strip()},
        }
