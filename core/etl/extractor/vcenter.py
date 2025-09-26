# ----------------------------------------------------------------------
# VMWare vCenter Extractors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import enum
from typing import Iterable, Optional, List, Tuple, Union

# Third-party modules
from pyVmomi import vim
from pyVmomi import vmodl
from pyVim.connect import Disconnect, SmartConnect

# NOC modules
from noc.core.etl.extractor.base import BaseExtractor
from noc.core.etl.models.typing import ETLMapping, MappingItem, RemoteReference
from noc.core.etl.remotesystem.base import BaseRemoteSystem
from noc.core.etl.models.managedobject import ManagedObject, CapsItem
from noc.core.etl.models.resourcegroup import ResourceGroup
from noc.core.etl.models.object import Object, ObjectData
from noc.core.etl.models.link import Link
from noc.core.etl.models.fmevent import FMEventObject, Var, RemoteObject
from noc.core.fm.event import EventSeverity
from noc.core.validators import is_ipv4, is_fqdn
from noc.core.ip import IP


class AlarmStatus(enum.Enum):
    gray = "gray"
    green = "green"
    yellow = "yellow"
    red = "red"


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
        net_view.Destroy()


@VCenterRemoteSystem.extractor
class VCenterManagedObjectExtractor(VCenterExtractor):
    name = "managedobject"
    model = ManagedObject

    def __init__(self, system):
        super().__init__(system)
        self.links = []

    def get_mappings(self, obj: Union[vim.VirtualMachine, vim.HostSystem]) -> List[MappingItem]:
        """Additional mappings"""
        return []

    def get_administrative_domain(
        self, obj: Union[vim.VirtualMachine, vim.HostSystem]
    ) -> Union[str, ETLMapping, RemoteReference]:
        """Detect ManagedObject"""
        return ETLMapping(value="default", scope="adm_domain")

    def get_labels(self, obj: Union[vim.VirtualMachine, vim.HostSystem]) -> List[str]:
        """Additional mappings"""
        return []

    def get_vm_address(self, obj: vim.VirtualMachine) -> Optional[str]:
        """Parse VM Management Address"""
        if not obj.guest or not obj.guest.ipAddress:
            return None
        if (
            not obj.guest.ipAddress.startswith("10.0.0.")
            and is_ipv4(obj.guest.ipAddress)
            and not IP.prefix(obj.guest.ipAddress).is_link_local
        ):
            return obj.guest.ipAddress
        addresses = []
        for net in obj.guest.net:
            for a in net.ipAddress:
                if is_ipv4(a) and not a.startswith("10.0.0.") and not IP.prefix(a).is_link_local:
                    addresses.append(a)
        return addresses[0] if addresses else None

    def get_host_mgmt_address(self, obj: vim.HostSystem) -> Optional[str]:
        """Parse Management Address"""
        name, *domains = obj.summary.config.name.split(".", 1)
        addrs = [vv.spec.ip.ipAddress for vv in obj.config.network.vnic]
        if len(addrs) > 1:
            self.logger.debug("[%s] Multiple Addresses on Host: %s", name, addrs)
        if name.startswith("rtm"):
            addrs = sorted(addrs)
        if addrs:
            return addrs[0]
        return None

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
            fqdn=f"{self.url}." if is_fqdn(self.url) else None,
            auth_profile=ETLMapping(value="default.vcenter", scope="auth_profile"),
            administrative_domain=ETLMapping(value="default", scope="adm_domain"),
            object_profile=ETLMapping(value="host.vcenter.default", scope="objectprofile"),
            pool="default",
            segment=ETLMapping(value="ALL", scope="segment"),
            scheme="4",
        )
        for h in host_view.view:
            host_map[h._moId] = h.summary.hardware.uuid
            if h.runtime.powerState != "poweredOn":
                continue
            name, *domains = h.summary.config.name.split(".", 1)
            if not h.summary.hardware.uuid:
                self.register_quality_problem(
                    int(h._moId[5:]),
                    "VMWOGLOBALID",
                    "VMachine without Global Id",
                    [],
                )
                continue
            mappings = self.get_mappings(h)
            yield ManagedObject(
                id=h.summary.hardware.uuid,
                name=name,
                address=self.get_host_mgmt_address(h),
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
                mappings=mappings or None,
                # static_service_groups=[str(r_type.value)],
            )
        host_view.Destroy()
        vm_view = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.VirtualMachine], True
        )
        for vm in vm_view.view:
            op = ETLMapping(value="host.default", scope="objectprofile")
            if not vm.config:
                self.logger.warning("[%s] VM without config", vm._moId)
                continue
            elif not vm.config.uuid:
                self.register_quality_problem(
                    int(vm._moId[3:]),
                    "VMWOGLOBALID",
                    "VMachine without Global Id",
                    [],
                )
                continue
            address = self.get_vm_address(vm)
            if not address:
                op = ETLMapping(value="host.vm.disabled", scope="objectprofile")
            name = vm.config.name
            if name in names:
                name = f"{name}#{vm._moId}"
            mappings = self.get_mappings(vm)
            wf_event = "power_on"
            if vm.runtime.powerState == "poweredOff":
                wf_event = "power_off"
            elif vm.runtime.powerState == "suspended":
                wf_event = "pause"
            yield ManagedObject(
                id=vm.config.uuid,
                name=name,
                event=wf_event,
                address=address,
                # description=description,
                profile="VMWare.vMachine",
                administrative_domain=self.get_administrative_domain(vm),
                object_profile=op,
                pool="default",
                controller=vcenter_uuid,
                segment=ETLMapping(value="ALL", scope="segment"),
                scheme="4",
                capabilities=[
                    CapsItem(name="VMWare | VM | GlobalId", value=vm.config.uuid),
                    CapsItem(name="Controller | LocalId", value=vm._moId),
                    CapsItem(name="Controller | GlobalId", value=vm.config.uuid),
                ],
                mappings=mappings or None,
                labels=self.get_labels(vm) or None,
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


@VCenterRemoteSystem.extractor
class VCenterFMEventExtractor(VCenterExtractor):
    """
    Extract Device Roles from NetBox
    """

    name = "fmevent"
    model = FMEventObject

    def get_object(
        self, event: vim.event.Event, content: vim.ServiceInstanceContent
    ) -> "RemoteObject":
        """"""
        if event.vm:
            return RemoteObject(name=event.vm.name, remote_id=event.vm.vm.config.uuid)
        elif event.host:
            return RemoteObject(
                name=event.host.name,
                remote_id=event.host.host.summary.hardware.uuid,
            )
        return RemoteObject(
            name=self.url,
            address=content.sessionManager.currentSession.ipAddress,
            remote_id=content.about.instanceUuid,
        )

    def parse_data(self, event: vim.event.Event) -> Tuple[str, List[Var]]:
        """"""
        message, r = None, []
        if event.userName:
            r.append(Var(name="username", value=event.userName))
        for p in event._propList:
            v = getattr(event, p.name)
            if not v:
                continue
            elif isinstance(v, vim.event.HostEventArgument):
                v = v.name
            elif hasattr(v, "name"):
                v = v.name
            if p.name in ("source", "entity"):
                continue
            elif p.name == "message":
                message = v
            elif p.name in ("arguments", "info"):
                # info - taskInfo
                continue
            else:
                r.append(Var(name=p.name, value=str(v)))
        # if isinstance(event, vim.event.AlarmStatusChangedEvent):
        #     print(
        #         "xxxxxxxxx",
        #         event.alarm.name,
        #         event.alarm.alarm.info.key,
        #         event.alarm.alarm.info.systemName,
        #         event.alarm.alarm.info.description,
        #     )
        #    for a in event.source.entity.triggeredAlarmState:
        #        print("AA", a.key, a.alarm.info.creationEventId, a.alarm.info)

        return message, r

    def get_event_type_filter(self) -> List[str]:
        """Return list event types for extract"""
        return [
            "AlarmClearedEvent",
            "AlarmCreatedEvent",
            "AlarmEvent",
            "AlarmRemovedEvent",
            "AlarmStatusChangedEvent",
            "ClusterEvent",
            "DatacenterEvent",
            "DatastoreEvent",
            "EnteredMaintenanceModeEvent",
            "EnteringMaintenanceModeEvent",
            "EnteredStandbyModeEvent",
            "EnteringStandbyModeEvent",
            "GeneralHostErrorEvent",
            # "GeneralHostWarningEvent",
            "MigrationEvent",
            # "TaskEvent",
            "VmCreatedEvent",
            "VmDasBeingResetEvent",
            "VmDiskFailedEvent",
            "VmFailedRelayoutEvent",
            "VmFailedToPowerOffEvent",
            "VmFailedToPowerOnEvent",
            "VmRegisteredEvent",
            "VmStartingEvent",
            "VmStoppingEvent",
            "VmSuspendedEvent",
            "VmSuspendingEvent",
            "VmGuestRebootEvent",
            "VmGuestShutdownEvent",
            "VmGuestStandbyEvent",
            "VmPoweredOffEvent",
            "VmPoweredOnEvent",
            "VmMigratedEvent",
            "VmRelocatedEvent",
            # "Event",
        ]

    def iter_data(self, checkpoint=None, **kwargs) -> Iterable[FMEventObject]:
        content = self.connection.RetrieveContent()
        # alarm = content.alarmManager.GetAlarm()
        # for a in alarm:
        #    print(a.info.key, a.info.description, a.info.systemName)
        # print(alarm)
        # for ta in content.rootFolder.triggeredAlarmState:
        #    print(ta.alarm.info.name+','+ta.entity.name+','+ta.overallStatus+','+str(ta.time))
        # by_entity = vim.event.EventFilterSpec.ByEntity(entity=vm, recursion="self")
        #     ids = ['VmRelocatedEvent', 'DrsVmMigratedEvent', 'VmMigratedEvent']
        #     filter_spec = vim.event.EventFilterSpec(entity=by_entity, eventTypeId=ids)
        # Time Filter
        time_filter = vim.event.EventFilterSpec.ByTime()
        time_filter.endTime = datetime.datetime.now()
        time_filter.beginTime = datetime.datetime.now() - datetime.timedelta(hours=24)
        # Event IDS
        ids = self.get_event_type_filter()
        event_filter = vim.event.EventFilterSpec(time=time_filter, eventTypeId=ids)
        collector = content.eventManager.CreateCollector(event_filter)

        vms_not_found = set()

        while True:
            try:
                events = collector.ReadNext(20)
            except (KeyError, TypeError) as e:
                self.logger.error("Unknown server error: %s", e)
                continue
            if not events:
                break
            for event in events:
                # ts = datetime.datetime.fromisoformat(event.createdTime)
                if not hasattr(event, "severity") or not event.severity:
                    severity = EventSeverity.INDETERMINATE
                else:
                    severity = EventSeverity.WARNING
                if event.vm and event.vm.name in vms_not_found:
                    continue
                msg, data = self.parse_data(event)
                try:
                    obj = self.get_object(event, content)
                except vmodl.fault.ManagedObjectNotFound:
                    self.logger.info("VM Not Found: %s", event.vm.name)
                    if event.vm:
                        vms_not_found.add(event.vm.name)
                    continue
                yield FMEventObject(
                    id=str(event.key),
                    ts=int(event.createdTime.timestamp()),
                    object=obj,
                    event_class=str(event.__class__.__name__),
                    severity=severity,
                    message=event.fullFormattedMessage or msg,
                    data=data,
                )
        Disconnect(self.connection)
