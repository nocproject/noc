# ----------------------------------------------------------------------
# ifdesc check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Tuple, Dict

# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck
from noc.core.validators import is_ipv4
from noc.inv.models.interface import Interface
from noc.inv.models.ifdescpatterns import IfDescPatterns
from noc.inv.models.discoveryid import DiscoveryID
from noc.main.models.handler import Handler
from noc.sa.models.managedobject import ManagedObject


class IfDescCheck(TopologyDiscoveryCheck):
    """
    IfDesc Topology discovery
    """

    name = "ifdesc"
    OBJ_REF_NAMES = {"name", "address", "hostname"}
    IFACE_REF_NAMES = {"interface", "ifindex"}
    MAX_MO_CANDIDATES = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.if_cache: Dict[int, Dict[str, Interface]] = {}

    def handler(self):
        candidates: List[Tuple[Interface, Interface]] = []
        ifaces = self.get_object_interfaces(self.object)
        for iface in ifaces.values():
            ri = self.resolve_remote_interface(iface)
            if ri:
                self.logger.info(
                    "Candidate link: %s:%s -- %s:%s",
                    iface.managed_object.name,
                    iface.name,
                    ri.managed_object.name,
                    ri.name,
                )
                candidates += [(iface, ri)]
        # Check other side
        if self.object.object_profile.ifdesc_symmetric:
            confirmed: List[Tuple[Interface, Interface]] = []
            for li, ri in candidates:
                riri = self.resolve_remote_interface(ri)
                if not riri:
                    self.logger.info(
                        "Failed symmetric check: %s:%s -- %s:%s, not found, ignoring",
                        li.managed_object.name,
                        li.name,
                        ri.managed_object.name,
                        ri.name,
                    )
                    continue
                if riri.managed_object.id != self.object.id:
                    self.logger.info(
                        "Failed symmetric check: %s:%s -- %s:%s, leading to other object %s, ignoring",
                        li.managed_object.name,
                        li.name,
                        ri.managed_object.name,
                        ri.name,
                        riri.managed_object.name,
                    )
                    continue
                if riri.name != li.name:
                    self.logger.info(
                        "Failed symmetric check: %s:%s -- %s:%s, leading to other interface %s, ignoring",
                        li.managed_object.name,
                        li.name,
                        ri.managed_object.name,
                        ri.name,
                        riri.name,
                    )
                    continue
                confirmed += [(li, ri)]
            candidates = confirmed
        # Link remaining
        for li, ri in candidates:
            self.confirm_link(li.managed_object, li.name, ri.managed_object, ri.name)

    def resolve_remote_interface(self, iface: Interface) -> Optional[Interface]:
        direction = "local" if iface.managed_object.id == self.object.id else "remote"
        if not iface.description or not iface.description.strip():
            self.logger.info("%s interface %s has no description. Ignoring", direction, iface.name)
            return None
        if iface.type != "physical":
            self.logger.info(
                "%s interface %s has invalid type %s. Ignoring", direction, iface.name, iface.type
            )
            return None
        # Try Interface Profile Handler
        if_prof = iface.get_profile()
        if if_prof.ifdesc_handler:
            ri = self.resolve_via_handler(if_prof.ifdesc_handler, iface)
            if ri:
                return ri
        # Try Interface Profile Patterns
        if if_prof.ifdesc_patterns:
            ri = self.resolve_via_patterns(if_prof.ifdesc_patterns, iface)
            if ri:
                return ri
        # Try Object Profile Handler
        if self.object.object_profile.ifdesc_handler:
            ri = self.resolve_via_handler(self.object.object_profile.ifdesc_handler, iface)
            if ri:
                return ri
        # Try Object Profile Patterns
        if self.object.object_profile.ifdesc_patterns:
            ri = self.resolve_via_patterns(self.object.object_profile.ifdesc_patterns, iface)
            if ri:
                return ri
        # Not found
        return None

    def resolve_via_handler(self, hi: Handler, iface: Interface) -> Optional[Interface]:
        """
        Try to resolve remote interface via handler
        :param hi:
        :param iface:
        :return:
        """
        handler = hi.get_handler()
        return handler(self.object, iface)

    def resolve_via_patterns(
        self, patterns: IfDescPatterns, iface: Interface
    ) -> Optional[Interface]:
        self.logger.debug(
            "[%s] Checking patterns %s for '%s'", iface.name, patterns.name, iface.description
        )
        for matches in patterns.iter_match(iface.description):
            self.logger.debug("Matches %s", matches)
            obj_ref = {n: matches[n] for n in matches if n in self.OBJ_REF_NAMES}
            if not obj_ref:
                self.logger.debug(
                    "No object reference extracted. At least one of the %s must be present",
                    ", ".join(self.OBJ_REF_NAMES),
                )
                continue
            ro, ifdescrtoken = self.resolve_object_via_patterns(iface.managed_object, **obj_ref)
            if not ro:
                self.logger.debug("Object cannot be resolved. Skipping")
                continue
            iface_ref = {n: matches[n] for n in matches if n in self.IFACE_REF_NAMES}
            if patterns.resolve_remote_port_by_object and ifdescrtoken:
                iface_ref["ifdescrtoken"] = ifdescrtoken
            if not iface_ref:
                self.logger.debug(
                    "No interface reference extracted. At least one of the %s must be present",
                    ", ".join(self.IFACE_REF_NAMES),
                )
                continue
            self.logger.debug("Resolve interface via patterns %s", iface_ref)
            ri = self.resolve_interface_via_patterns(ro, **iface_ref)
            if not ri:
                self.logger.debug("Interface cannot be resolved. Skipping")
            return ri
        return None

    def resolve_object_via_patterns(
        self,
        lmo: ManagedObject,
        name: Optional[str] = None,
        address: Optional[str] = None,
        hostname: Optional[str] = None,
    ) -> Tuple[Optional[ManagedObject], Optional[str]]:
        def get_nearest_object(objects: List[ManagedObject]) -> Optional[ManagedObject]:
            # Prefer same pool
            left = [x for x in objects if x.is_managed and x.pool.id == lmo.pool.id]
            if len(left) == 1:
                return left[0]
            # Prefer same segment
            left = [x for x in objects if x.is_managed and x.segment.id == lmo.segment.id]
            if len(left) == 1:
                return left[0]
            return None

        if name:
            # Full name match
            mo = ManagedObject.objects.filter(name=name).first()
            if mo:
                return mo, lmo.name
            # Partial name match
            if "#" not in name:
                mos = ManagedObject.objects.filter(name__startswith=name + "#")[
                    : self.MAX_MO_CANDIDATES
                ]
                mo = get_nearest_object(mos)
                if mo:
                    return mo, lmo.name
        if address and not is_ipv4(address):
            self.logger.warning("Unknown IPv4 address format: %s", address)
        elif address:
            # Address match
            mos = ManagedObject.objects.filter(address=address)[: self.MAX_MO_CANDIDATES]
            mo = get_nearest_object(mos)
            if mo:
                return mo, lmo.address
        if hostname:
            did = DiscoveryID.objects.filter(object=lmo).first()
            mo = self.get_neighbor_by_hostname(hostname)
            if mo:
                return mo, did.hostname if did else ""
        return None, None

    def resolve_interface_via_patterns(
        self,
        mo: ManagedObject,
        interface: Optional[str] = None,
        ifindex: Optional[str] = None,
        ifdescrtoken: Optional[str] = None,
    ) -> Optional[Interface]:
        ifaces = self.get_object_interfaces(mo)
        if not ifaces:
            if interface:
                # Object has no interfaces but may allow to auto-create one
                return self.maybe_create_interface(mo, interface)
            return None
        if interface:
            try:
                interface = self.get_remote_interface(mo, interface)
            except ValueError as e:
                self.logger.warning(
                    "Error getting remote interface by name '%s' (%s)", interface, e
                )
                interface = None
            if interface:
                iface = ifaces.get(interface)
                if iface:
                    return iface
                # Target interface is not found, but object may allow to auto-create one
                return self.maybe_create_interface(mo, interface)
        if ifindex:
            ifi = int(ifindex)
            matched = [x for x in ifaces.values() if x.ifindex == ifi]
            if len(matched) == 1:
                return matched[0]
        if ifdescrtoken:
            # Get interface by token
            ifaces = list(
                Interface.objects.filter(
                    managed_object=mo.id, type="physical", description__icontains=ifdescrtoken
                )
            )
            if len(ifaces) == 1:
                return ifaces[0]
            self.logger.warning(
                "Not found interface by token '%s' (found %d)", ifdescrtoken, len(ifaces)
            )
        return None

    def get_object_interfaces(self, mo: ManagedObject) -> Dict[str, Interface]:
        ifaces = self.if_cache.get(mo.id)
        if ifaces is not None:
            return ifaces
        ifaces = {
            x.name: x for x in Interface.objects.filter(managed_object=mo.id, type="physical")
        }
        self.if_cache[mo.id] = ifaces
        return ifaces

    def maybe_create_interface(self, mo: ManagedObject, name: str) -> Optional[Interface]:
        """
        Auto-create remote interface, if possible

        :param mo:
        :param name:
        :return:
        """
        if self.object.object_profile.ifdesc_symmetric:
            return None  # Meaningless for symmetric ifdesc
        if (
            mo.object_profile.enable_box_discovery_interface
            or not mo.object_profile.enable_interface_autocreation
        ):
            return None  # Auto-creation is disabled
        # Create interface
        self.logger.info("Auto-creating interface %s:%s", mo.name, name)
        iface = Interface(managed_object=mo, type="physical", name=name)
        iface.save()
        # Adjust cache
        if mo.id in self.if_cache:
            self.if_cache[mo.id][iface.name] = iface
        return iface
