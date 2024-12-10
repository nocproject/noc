# ----------------------------------------------------------------------
# VIM methods implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Any

# Third-party modules
from pyVim.connect import Disconnect, SmartConnect
from pyVmomi import vim

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.script.base import BaseScript
from noc.core.error import NOCError, ERR_HTTP_UNKNOWN


class VIMError(NOCError):
    default_code = ERR_HTTP_UNKNOWN


class VIM(object):
    VIMError = VIMError

    def __init__(self, script):
        self.script = script
        if script:  # For testing purposes
            self.logger = PrefixLoggerAdapter(script.logger, "vim")
        self.connection: Optional[vim.ServiceInstance] = None
        self._content: Optional[Any] = None

    def ensure_session(self):
        if not self.connection:
            self.setup_session()

    def setup_session(self):
        if self.script.controller:
            self.connection = SmartConnect(
                host=self.script.controller.address,
                user=self.script.controller.user,
                pwd=self.script.controller.password,
                disableSslCertValidation=True,
            )
        else:
            self.connection = SmartConnect(
                host=self.script.credentials["address"],
                user=self.script.credentials.get("user"),
                pwd=self.script.credentials.get("password"),
                disableSslCertValidation=True,
            )

    def shutdown_session(self):
        self.logger.debug("Shutdown VIM session")
        self.connection = None

    def get_connection(self) -> "vim.ServiceInstance":
        self.ensure_session()
        return self.connection

    def close(self):
        self.logger.debug("Close VIM connection")
        # self.connection.content.sessionManager.Logout()
        if self.connection:
            Disconnect(self.connection)

    @property
    def content(self):
        if self._content:
            return self._content
        self._content = self.get_connection().content
        #         except vim.fault.NotAuthenticated:
        #             raise VIMError("Not Authenticated")
        # connection.content.sessionManager.message
        return self._content

    @property
    def about(self):
        return self.content.about

    def get_host_by_id(self, hid: str) -> vim.HostSystem:
        """Getting vCenter host by id, example: 'host-5260'"""
        search_index = self.content.searchIndex
        try:
            h = search_index.FindByUuid(None, hid, False)
        except vim.fault.NotAuthenticated:
            raise VIMError("Not Authenticated")
        if not h:
            raise VIMError("Virtual Machine with Id '%s' Not found" % hid)
        return h

    def get_vm_by_id(self, vid: str) -> Optional[vim.VirtualMachine]:
        """Getting vMachine by id, example: 'vm-1030'"""
        search_index = self.content.searchIndex
        vm = search_index.FindByUuid(None, vid, True)
        if not vm:
            raise VIMError("Virtual Machine with Id '%s' Not found" % vid)
        return vm

    def get_vm_by_name(self, name: str) -> Optional[vim.VirtualMachine]:
        vm_view = self.content.viewManager.CreateContainerView(
            self.content.rootFolder,
            [vim.VirtualMachine],
            True,
        )
        try:
            vms = [h for h in vm_view.view if h.name == name]
        except vim.fault.NotAuthenticated:
            raise VIMError("Not Authenticated")
        vm_view.Destroy()
        if vms:
            return vms[0]
        else:
            raise VIMError("Host %s Not found" % name)

    @staticmethod
    def has_internet_adapter(item) -> bool:
        return isinstance(item, vim.vm.device.VirtualEthernetCard)


class VIMScript(BaseScript):
    @property
    def vim(self):
        if hasattr(self, "_vim"):
            return self._vim
        if self.parent and hasattr(self.parent, "vim"):
            self._vim = self.root.vim
        else:
            self._vim = VIM(self)
        return self._vim

    def close_cli_stream(self):
        super().close_cli_stream()
        if hasattr(self, "_vim"):
            # Close VIM Client
            self.vim.close()
            delattr(self, "_vim")
