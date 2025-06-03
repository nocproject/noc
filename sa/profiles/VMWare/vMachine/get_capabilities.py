# ---------------------------------------------------------------------
# VMWare.vMachine.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from ..vim import VIMScript


class Script(BaseScript, VIMScript):
    name = "VMWare.vMachine.get_capabilities"

    GB = 1024**3

    def execute_platform_cli(self, caps):
        self.logger.info("Execute Platform")
        vm = self.vim.get_vm_by_id(self.controller.global_id)
        caps |= {
            "VM | vCPU": vm.summary.config.numCpu,
            "VM | vRAM": round(vm.summary.config.memorySizeMB / 1024),
            "VM | vHDD": round(
                (vm.summary.storage.uncommitted + vm.summary.storage.unshared) / self.GB, 3
            ),
            "VM | Tools Status": vm.summary.guest.toolsStatus,
        }
        if vm.summary.guest.toolsStatus not in {"toolsOk", "toolsOld"}:
            return
        si = vm.guest.ipStack[0]
        if si.dnsConfig and si.dnsConfig.ipAddress:
            caps["VM | DNS Servers"] = ",".join(si.dnsConfig.ipAddress)
        dg = [x.gateway.ipAddress for x in si.ipRouteConfig.ipRoute if x.network == "0.0.0.0"]
        if dg:
            caps["VM | Gateway"] = dg[0]
