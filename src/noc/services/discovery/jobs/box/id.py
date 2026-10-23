# ---------------------------------------------------------------------
# ID check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.mac import MAC
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.discoveryid import DiscoveryID, MACRange


class IDCheck(DiscoveryCheck):
    """
    Version discovery
    """

    name = "id"
    required_script = "get_discovery_id"

    def handler(self):
        self.logger.info("Checking chassis id")
        result = self.object.scripts.get_discovery_id()
        cm = result.get("chassis_mac")
        interface_macs = self.get_artefact("interface_macs")
        self.logger.info(
            "Identity found: "
            "Chassis MACs = %s, hostname = %s, router-id = %s, "
            "additional MACs = %s",
            self.format_range(cm),
            result.get("hostname"),
            result.get("router_id"),
            ", ".join(interface_macs or []),
        )
        # Sanitize MAC ranges, may be too broad and consume large amount of memory
        chassis_mac = []
        if cm:
            for item in cm:
                try:
                    chassis_mac.append(self.clean_range(item))
                except ValueError as e:
                    self.logger.error(
                        "Invalid MAC range %s - %s: %s",
                        item["first_chassis_mac"],
                        item["last_chassis_mac"],
                        e,
                    )
            if not chassis_mac:
                self.logger.error("All MAC ranges failed, check get_discovery_id script")

        DiscoveryID.submit(
            object=self.object,
            chassis_mac=chassis_mac,
            hostname=result.get("hostname"),
            router_id=result.get("router_id"),
            additional_macs=interface_macs,
        )

    @staticmethod
    def format_range(r: list[dict[str, str]] | None) -> str:
        """Format MAC range for logging."""

        def q(r: dict[str, str]) -> str:
            return f"{r['first_chassis_mac']} - {r['last_chassis_mac']}"

        if not r:
            return "None"
        return ", ".join(q(x) for x in r)

    def clean_range(self, r: dict[str, str]) -> MACRange:
        """
        Sanitize MAC range.
        """
        s = MAC(r["first_chassis_mac"])
        e = MAC(r["last_chassis_mac"])
        if s > e:
            s, e = e, s  # Swap
        if not MAC.is_same_oui(s, e):
            raise ValueError("not belongs to same OUI")
        if config.discovery.max_id_mac_range > 0:
            d = MAC.distance(s, e)
            if d > config.discovery.max_id_mac_range:
                msg = f"too broad range {d} macs (max {config.discovery.max_id_mac_range} allowed)"
                raise ValueError(msg)
        return MACRange(first_mac=str(s), last_mac=str(e))
