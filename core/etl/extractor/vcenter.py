# ----------------------------------------------------------------------
# VMWare vCenter Extractors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Iterable, Optional, List

# Third-party modules
from pyVmomi import vim
from pyVim.connect import Disconnect, SmartConnect

# NOC modules
from noc.core.etl.extractor.base import BaseExtractor
from noc.core.etl.models.typing import ETLMapping
from noc.core.etl.remotesystem.base import BaseRemoteSystem
from noc.core.etl.models.managedobject import ManagedObject, CapsItem
from noc.core.etl.models.resourcegroup import ResourceGroup
from noc.core.etl.models.object import Object, ObjectData
from noc.core.etl.models.link import Link
from noc.core.validators import is_ipv4


class VCenterRemoteSystem(BaseRemoteSystem):
    """

    Configuration variables (Main -> Setup -> Remote System -> Environments)
    API_URL - host address of fqdn for vCenter
    API_USER - username for ro access to device
    API_PASSWORD - password for user access
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

    @staticmethod
    def has_internet_adapter(item) -> bool:
        return isinstance(item, vim.vm.device.VirtualEthernetCard)

    # def list_vms(self):
    #     content = self.connection.content
    #     container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    #     return [VirtualMachine(managed_object_ref) for managed_object_ref in container.view]


@VCenterRemoteSystem.extractor
class VCenterLinkExtractor(BaseExtractor):
    name = "link"
    model = Link

    def __init__(
        self,
        system: "VCenterRemoteSystem",
        config=None,
        links: List[Link] = None,
    ):
        super().__init__(system)
        self.links = links or []

    def extract(self, incremental: bool = False, **kwargs) -> None:
        return

    def extract_data(self, incremental=False):
        super().extract(incremental=incremental)

    def iter_data(self, *, checkpoint: Optional[str] = None, **kwargs) -> Iterable[Link]:
        yield from self.links


@VCenterRemoteSystem.extractor
class VCenterObjectExtractor(VCenterExtractor):
    name = "object"
    model = Object

    def iter_data(self, *, checkpoint: Optional[str] = None, **kwargs) -> Iterable[Object]:
        content = self.connection.content
        vm_view = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.HostSystem], True
        )
        yield Object(id="vcenter.root", name="VCenter vMachines", model="Group")
        for vm in vm_view.view:
            yield Object(
                id=vm.config.uuid,
                name=vm.config.name,
                model="VMWare | Virtual Platform | VMX19",
                data=[
                    ObjectData(
                        interface="asset",
                        attr="serial",
                        value=vm.config.uuid,
                        scope=self.system.remote_system.name,
                    ),
                ],
                parent="vcenter.root",
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

    def __init__(self, system):
        super().__init__(system)
        self.links = []

    def parse_address(self, guest: vim.vm.GuestInfo) -> str:
        addresses = []
        for n in guest.net:
            addresses += [a for a in n.ipAddress if is_ipv4(a) and not a.startswith("10.0.0.")]
        return addresses[0]

    def iter_data(self, checkpoint=None, **kwargs) -> Iterable[ManagedObject]:
        host_map = {}
        content = self.connection.content
        host_view = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.HostSystem], True
        )
        vcenter_uuid = content.about.instanceUuid
        names = set()
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
            host_map[h._moId] = h.summary.hardware.uuid
            addrs = [vv.spec.ip.ipAddress for vv in h.config.network.vnic]
            if len(addrs) > 1:
                self.logger.debug("[%s] Multiple Addresses on Host: %s", name, addrs)
            yield ManagedObject(
                id=h.summary.hardware.uuid,
                name=name,
                address=addrs[0],
                # description=description,
                profile="VMWare.vHost",
                administrative_domain=ETLMapping(value="default", scope="adm_domain"),
                object_profile=ETLMapping(value="host.hypervisor.default", scope="objectprofile"),
                pool="default",
                controller=vcenter_uuid,
                segment=ETLMapping(value="ALL", scope="segment"),
                scheme="4",
                capabilities=[
                    CapsItem(name="Controller | LocalId", value=h._moId),
                    CapsItem(name="Controller | GlobalId", value=h.summary.hardware.uuid),
                ],
                # static_service_groups=[str(r_type.value)],
            )
        host_view.Destroy()
        vm_view = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.VirtualMachine], True
        )
        for vm in vm_view.view:
            address = "0.0.0.0"
            op = ETLMapping(value="host.default", scope="objectprofile")
            if not vm.config:
                self.logger.warning("[%s] VM without config", vm._moId)
                continue
            if vm.guest and vm.guest.ipAddress:
                address = self.parse_address(vm.guest)
            else:
                op = ETLMapping(value="host.vm.disabled", scope="objectprofile")
            name = vm.config.name
            if name in names:
                name = f"{name}#{vm._moId}"
            yield ManagedObject(
                id=vm.config.uuid,
                name=name,
                address=address,
                # description=description,
                profile="VMWare.vMachine",
                administrative_domain=ETLMapping(value="default", scope="adm_domain"),
                object_profile=op,
                pool="default",
                controller=vcenter_uuid,
                segment=ETLMapping(value="ALL", scope="segment"),
                scheme="4",
                capabilities=[
                    CapsItem(name="Controller | LocalId", value=vm._moId),
                    CapsItem(name="Controller | GlobalId", value=vm.config.uuid),
                ],
            )
            names.add(name)
            for d in vm.config.hardware.device:
                if (
                    self.has_internet_adapter(d)
                    and hasattr(d.backing, "port")
                    and d.backing.port.portKey
                ):
                    self.links.append(
                        Link(
                            id=f"{d.key}_{vm.runtime.host._moId}_{d.backing.port.portKey}",
                            source=self.system.remote_system.name,
                            src_mo=vm.config.uuid,
                            src_interface=f"vmnic-{d.key}",
                            dst_mo=host_map[vm.runtime.host._moId],
                            dst_interface=f"vmnic-{d.backing.port.portKey}",
                        )
                    )
        Disconnect(self.connection)

    def extract(self, incremental: bool = False, **kwargs) -> None:
        """Override default behavior, do not clear import file"""
        super().extract(incremental=incremental)
        mol = VCenterLinkExtractor(self.system, links=self.links)
        mol.extract_data(incremental=incremental)
