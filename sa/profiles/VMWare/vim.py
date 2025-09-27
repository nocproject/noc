# ----------------------------------------------------------------------
# VIM methods implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Any

# Third-party modules
from pyVmomi import vim

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.script.base import BaseScript
from noc.core.error import NOCError, ERR_HTTP_UNKNOWN
from .connection import connect, disconnect


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

    def get_session_alias(self):
        if self.script.controller:
            return self.script.controller.address
        return self.script.credentials["address"]

    def get_args(self):
        if self.script.controller:
            return {
                "host": self.script.controller.address,
                "alias": self.get_session_alias(),
                "username": self.script.controller.user,
                "password": self.script.controller.password,
            }
        return {
            "host": self.script.credentials["address"],
            "alias": self.get_session_alias(),
            "username": self.script.credentials.get("user"),
            "password": self.script.credentials.get("password"),
        }

    def shutdown_session(self):
        self.logger.debug("Shutdown VIM session")
        self.connection = None
        self._content = None

    def get_connection(self) -> "vim.ServiceInstance":
        if not self.connection:
            self.connection = connect(**self.get_args())
        #         except vim.fault.NotAuthenticated:
        #             raise VIMError("Not Authenticated")
        return self.connection

    def refresh_session(self):
        """Try Login"""
        # Use SessionId from Prev Session
        self.close()
        self.get_connection()

    def close(self):
        self.logger.debug("Close VIM connection")
        disconnect(self.get_session_alias())
        self.shutdown_session()

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

    def find_by_uuid(self, oid, find_vm: bool = True):
        """Find by UUID"""
        search_index = self.content.searchIndex
        try:
            return search_index.FindByUuid(None, oid, find_vm, None)
        except vim.fault.NotAuthenticated:
            # Refresh session
            self.refresh_session()
        try:
            return search_index.FindByUuid(None, oid, find_vm, None)
        except vim.fault.NotAuthenticated:
            raise VIMError("Not Authenticated")

    def get_host_by_id(self, hid: str) -> vim.HostSystem:
        """Getting vCenter host by id, example: 'host-5260'"""
        h = self.find_by_uuid(hid, find_vm=False)
        if not h:
            raise VIMError("Host with Id '%s' Not found" % hid)
        return h

    def get_vm_by_id(self, vid: str) -> Optional[vim.VirtualMachine]:
        """Getting vMachine by id, example: 'vm-1030'"""
        vm = self.find_by_uuid(vid, find_vm=True)
        if not vm:
            raise VIMError("Virtual Machine with Id '%s' Not found" % vid)
        return vm

    def get_container_view(self, o_type) -> vim.view.ContainerView:
        """Context for destroy!, iterator?"""
        try:
            view = self.content.viewManager.CreateContainerView(
                self.content.rootFolder,
                [o_type],
                True,
            )
        except vim.fault.NotAuthenticated:
            raise VIMError("Not Authenticated")
        return view

    def get_vm_by_name(self, name: str) -> Optional[vim.VirtualMachine]:
        vm_view = self.get_container_view(vim.VirtualMachine)
        vms = [h for h in vm_view.view if h.name == name]
        vm_view.Destroy()
        if vms:
            return vms[0]
        raise VIMError("Host %s Not found" % name)

    @staticmethod
    def has_internet_adapter(item) -> bool:
        return isinstance(
            item,
            (
                vim.vm.device.VirtualEthernetCard,
                vim.vm.device.VirtualVmxnet,
                vim.vm.device.VirtualVmxnet3,
            ),
        )


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
            self._vim = None
