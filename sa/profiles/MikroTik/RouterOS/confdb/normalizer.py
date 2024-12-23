# ----------------------------------------------------------------------
# MikroTik.RouterOS config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, deferable
from noc.core.confdb.syntax.patterns import INTEGER, IPv4_PREFIX, IPv4_ADDRESS, AS_NUM, REST
from noc.core.validators import is_ipv4_prefix, is_ipv4


class RouterOSNormalizer(BaseNormalizer):
    @match("/system", "identity", "name", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[3])

    @match("/system", "clock", "time-zone-name", ANY)
    def normalize_time_zone_name(self, tokens):
        yield self.make_tz(tz_name=tokens[3])

    @match("/ip", "route", INTEGER, "dst-address", IPv4_ADDRESS)
    def normalize_route_dst_address(self, tokens):
        yield self.defer(f"ip.route.{tokens[2]}", route=tokens[4])

    @match("/ip", "route", INTEGER, "gateway", IPv4_ADDRESS)
    def normalize_route_gateway(self, tokens):
        if not is_ipv4(tokens[4]):
            return
        yield self.defer(
            f"ip.route.{tokens[2]}",
            self.make_inet_static_route_next_hop,
            route=deferable("route"),
            next_hop=tokens[4],
        )

    @match("/ip", "route", INTEGER, "type", "blackhole")
    def normalize_route_type_blackhole(self, tokens):
        yield self.defer(
            f"ip.route.{tokens[2]}", self.make_inet_static_route_discard, route=deferable("route")
        )

    @match("/ip", "address", INTEGER, "address", IPv4_PREFIX)
    def normalize_interface_address(self, tokens):
        if not is_ipv4_prefix(tokens[4]):
            return
        yield self.defer(
            f"ip.address.{tokens[2]}",
            self.make_unit_inet_address,
            interface=deferable("interface"),
            address=tokens[4],
        )

    @match("/ip", "address", INTEGER, "interface", ANY)
    def normalize_interface_address_interface(self, tokens):
        yield self.defer(f"ip.address.{tokens[2]}", interface=tokens[4])

    @match("/system", "ntp", "client", INTEGER, "enabled", ANY)
    def normalize_timesource(self, tokens):
        if tokens[5] == "yes":
            yield self.make_clock_source(source="ntp")

    @match("/system", "ntp", "client", ANY, ANY)
    def normalize_ntp_server(self, tokens):
        if tokens[3] == "primary-ntp":
            yield self.make_ntp_server_address(name="0", address=tokens[4])
        if tokens[3] == "secondary-ntp":
            yield self.make_ntp_server_address(name="1", address=tokens[4])

    @match("/routing", "bgp", "instance", ANY, "as", AS_NUM)
    def normalize_bgp_template_loca_as(self, tokens):
        yield self.defer(
            f"bgp.template.{tokens[3]}.local_as",
            as_num=tokens[5],
        )

    @match("/routing", "bgp", "instance", ANY, "router-id", ANY)
    def normalize_bgp_template_router_id(self, tokens):
        yield self.defer(
            f"bgp.template.{tokens[3]}.router_id",
            router_id=tokens[5],
        )

    @match("/routing", "bgp", "connection", INTEGER, "as", AS_NUM)
    def normalize_bgp_peer_local_as(self, tokens):
        yield self.defer(
            f"bgp.connection.{tokens[3]}.local_as",
            as_num=tokens[5],
        )

    @match("/routing", "bgp", "peer", INTEGER, "remote-as", AS_NUM)
    @match("/routing", "bgp", "connection", INTEGER, ".as", AS_NUM)
    def normalize_bgp_peer_as(self, tokens):
        yield self.defer(
            f"bgp.connection.{tokens[3]}",
            as_num=tokens[5],
        )

    @match("/routing", "bgp", "peer", INTEGER, "local-address", IPv4_PREFIX)
    @match("/routing", "bgp", "connection", INTEGER, "local.address", IPv4_PREFIX)
    def normalize_bgp_peer_local_address(self, tokens):
        yield self.defer(
            f"bgp.connection.{tokens[3]}",
            local_address=tokens[5],
        )

    @match("/routing", "bgp", "peer", INTEGER, ".role", ANY)
    @match("/routing", "bgp", "connection", INTEGER, ".role", ANY)
    def normalize_bgp_peer_role(self, tokens):
        role = "internal"
        if tokens[5] == "ebgp":
            role = "external"
        yield self.defer(
            f"bgp.connection.{tokens[3]}",
            role=role,
        )

    @match("/routing", "bgp", "peer", INTEGER, "name", ANY)
    @match("/routing", "bgp", "connection", INTEGER, "name", ANY)
    def normalize_bgp_peer_description(self, tokens):
        yield self.defer(
            f"bgp.connection.{tokens[3]}",
            description=tokens[5],
        )

    @match("/routing", "bgp", "peer", INTEGER, "out-filter", ANY)
    @match("/routing", "bgp", "connection", INTEGER, "output.filter-chain", ANY)
    def normalize_bgp_peer_out_filter(self, tokens):
        yield self.defer(
            f"bgp.connection.{tokens[3]}.export_filter",
            name=tokens[5],
        )

    @match("/routing", "bgp", "peer", INTEGER, "in-filter", ANY)
    @match("/routing", "bgp", "connection", INTEGER, "input.filter-chain", ANY)
    def normalize_bgp_peer_in_filter(self, tokens):
        yield self.defer(
            f"bgp.connection.{tokens[3]}.import_filter",
            name=tokens[5],
        )

    @match("/routing", "bgp", "network", INTEGER, "network", IPv4_PREFIX)
    def normalize_bgp_network(self, tokens):
        yield self.make_bgp_network(prefix=tokens[5])

    @match("/routing", "bgp", "peer", INTEGER, "disabled", "yes")
    def normalize_bgp_neighbor_admin_status(self, tokens):
        yield self.defer(
            f"bgp.connection.{tokens[3]}",
            admin_status=False,
        )

    @match("/routing", "bgp", "connection", INTEGER, "router-id", ANY)
    def normalize_bgp_neighbor_router_id(self, tokens):
        yield self.defer(
            f"bgp.connection.{tokens[3]}",
            router_id=tokens[5],
        )

    @match("/routing", "bgp", "peer", INTEGER, "remote-address", IPv4_PREFIX)
    @match("/routing", "bgp", "connection", INTEGER, "remote.address", IPv4_PREFIX)
    def normalize_bgp_peer_neighbor(self, tokens):
        yield self.make_bgp_neighbor(neighbor=tokens[5])
        yield self.make_bgp_neighbor_peer_group(neighbor=tokens[5], group="default")
        yield self.defer(
            f"bgp.connection.{tokens[3]}",
            self.make_bgp_neighbor_remote_as,
            neighbor=tokens[5],
            as_num=deferable("as_num"),
        )
        yield self.defer(
            f"bgp.connection.{tokens[3]}.local_as",
            self.make_bgp_neighbor_local_as,
            neighbor=tokens[5],
            as_num=deferable("as_num"),
        )
        yield self.defer(
            f"bgp.template.default.local_as",
            self.make_bgp_neighbor_local_as,
            neighbor=tokens[5],
            as_num=deferable("as_num"),
        )
        yield self.defer(
            f"bgp.connection.{tokens[3]}",
            self.make_bgp_neighbor_description,
            neighbor=tokens[5],
            description=deferable("description"),
        )
        yield self.defer(
            f"bgp.connection.{tokens[3]}.export_filter",
            self.make_bgp_neighbor_export_filter,
            neighbor=tokens[5],
            name=deferable("name"),
        )
        yield self.defer(
            f"bgp.connection.{tokens[3]}.import_filter",
            self.make_bgp_neighbor_import_filter,
            neighbor=tokens[5],
            name=deferable("name"),
        )
        yield self.defer(
            f"bgp.connection.{tokens[3]}",
            self.make_bgp_neighbor_type,
            neighbor=tokens[5],
            type=deferable("role"),
        )
        yield self.defer(
            f"bgp.connection.{tokens[3]}",
            self.make_bgp_neighbor_local_address,
            neighbor=tokens[5],
            address=deferable("local_address"),
        )
        yield self.defer(
            f"bgp.connection.{tokens[3]}",
            self.make_bgp_neighbor_admin_status,
            neighbor=tokens[5],
            admin_status=deferable("admin_status"),
        )
        yield self.defer(
            f"bgp.template.default.router_id",
            self.make_bgp_neighbor_router_id,
            neighbor=tokens[5],
            router_id=deferable("router_id"),
        )
        yield self.defer(
            f"bgp.connection.{tokens[3]}",
            self.make_bgp_neighbor_router_id,
            neighbor=tokens[5],
            router_id=deferable("router_id"),
        )

    @match("interface", "ethernet", ANY, "name", ANY)
    def normalize_interface_name(self, tokens):
        yield self.make_interface(
            interface=self.interface_name(tokens[2]),
        )

    @match("interface", "ethernet", ANY, "disabled", "yes")
    def normalize_interface_status(self, tokens):
        yield self.make_interface_admin_status(
            interface=self.interface_name(tokens[2]), admin_status=False
        )
