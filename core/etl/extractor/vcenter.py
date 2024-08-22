# ----------------------------------------------------------------------
# VMWare vCenter Extractors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable, Optional

# Third-party modules
from pyVmomi import vim
from pyVim.connect import Disconnect, SmartConnect

# NOC modules
from noc.core.etl.extractor.base import BaseExtractor
from noc.core.etl.models.typing import ETLMapping
from noc.core.etl.remotesystem.base import BaseRemoteSystem
from noc.core.etl.models.managedobject import ManagedObject, CapsItem
from noc.core.etl.models.resourcegroup import ResourceGroup
from noc.core.etl.models.object import Object  # , ObjectData


class VCenterRemoteSystem(BaseRemoteSystem):
    """

    Configuration variables (Main -> Setup -> Remote System -> Environments)
    API_URL - URL zabbix web interface
    API_USER - username for ro access to device
    API_PASSWORD - password for user access
    GROUPS_FILTER - list groups for extract
    """


class VCenterExtractor(BaseExtractor):
    """

    def iter_hosts():
        hosts = self.client.vcenter.Host.list()

        ...

    def iter_vm():
        self.client.vcenter.vm.guest.networking.Interfaces.list(x[1].vm)
    """

    def __init__(self, system):
        super().__init__(system)

        self.url = self.config.get("API_URL", None)
        self.connection = SmartConnect(
            host=self.url,
            user=self.config.get("API_USER"),
            pwd=self.config.get("API_PASSWORD"),
            disableSslCertValidation=True,
        )

    # def list_vms(self):
    #     content = self.connection.content
    #     container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    #     return [VirtualMachine(managed_object_ref) for managed_object_ref in container.view]


@VCenterRemoteSystem.extractor
class VCenterObjectExtractor(VCenterExtractor):
    name = "object"
    model = Object

    def iter_data(self, *, checkpoint: Optional[str] = None, **kwargs) -> Iterable[Object]:
        content = self.connection.content
        vm_view = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.HostSystem], True
        )
        for vm in vm_view.view:
            yield Object(
                id=vm.config.uuid,
                name=vm.config.name,
                model="",
                data=[],
                parent=None,
            )


@VCenterRemoteSystem.extractor
class VCenterResourceGroupExtractor(VCenterExtractor):
    """
    Extract PortGroup from VCenter
    """

    name = "resourcegroup"
    model = ResourceGroup

    def iter_data(self, checkpoint=None, **kwargs) -> Iterable[ResourceGroup]:
        yield ResourceGroup(
            id="vcenter.networks",
            name="VCenter Networks",
            technology="Group",
        )
        content = self.connection.content
        net_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.Network], True)
        for n in net_view.view:
            if isinstance(n, vim.Network):
                yield ResourceGroup(
                    id=n._moId,
                    name=n.name,
                    technology="VMWare | Port Group",
                    parent="vcenter.networks",
                )
                continue
            yield ResourceGroup(
                id=n.config.key,
                name=n.name,
                technology="VMWare | Port Group",
                description=n.config.description,
                parent="vcenter.networks",
            )


@VCenterRemoteSystem.extractor
class VCenterManagedObjectExtractor(VCenterExtractor):
    name = "managedobject"
    model = ManagedObject

    def iter_data(self, checkpoint=None, **kwargs) -> Iterable[ManagedObject]:
        content = self.connection.content
        host_view = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.HostSystem], True
        )
        vcenter_uuid = content.about.instanceUuid
        yield ManagedObject(
            id=vcenter_uuid,
            name=self.url,
            profile="VMWare.vCenter",
            address=content.sessionManager.currentSession.ipAddress,
            auth_profile=ETLMapping(value="default.vcenter", scope="auth_profile"),
            administrative_domain=ETLMapping(value="default", scope="adm_domain"),
            object_profile=ETLMapping(value="host.vcenter.default", scope="objectprofile"),
            pool="default",
            segment=ETLMapping(value="ALL", scope="segment"),
            scheme="4",
        )
        for h in host_view.view:
            if h.runtime.powerState != "poweredOn":
                continue
            name, *domains = h.summary.config.name.split(".", 1)
            yield ManagedObject(
                id=h.summary.hardware.uuid,
                name=name,
                address=h.config.network.vnic[0].spec.ip.ipAddress,
                # description=description,
                profile="VMWare.vHost",
                administrative_domain=ETLMapping(value="default", scope="adm_domain"),
                object_profile=ETLMapping(value="host.hypervisor.default", scope="objectprofile"),
                pool="default",
                controller=vcenter_uuid,
                segment=ETLMapping(value="ALL", scope="segment"),
                scheme="4",
                capabilities=[CapsItem(name="Controller | LocalId", value=h._moId)],
                # static_service_groups=[str(r_type.value)],
            )
        host_view.Destroy()
        vm_view = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.HostSystem], True
        )
        for vm in vm_view.view:
            address = "0.0.0.0"
            if vm.guest and vm.guest.ipAddress:
                address = vm.guest.ipAddress
            yield ManagedObject(
                id=vm.config.uuid,
                name=vm.config.name,
                address=address,
                # description=description,
                profile="VMWare.vMachine",
                administrative_domain=ETLMapping(value="default", scope="adm_domain"),
                object_profile=ETLMapping(value="host.default", scope="objectprofile"),
                pool="default",
                controller=vcenter_uuid,
                segment=ETLMapping(value="ALL", scope="segment"),
                scheme="4",
                capabilities=[CapsItem(name="Controller | LocalId", value=vm._moId)],
            )
        Disconnect(self.connection)
