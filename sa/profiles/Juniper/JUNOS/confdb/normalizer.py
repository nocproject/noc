# ----------------------------------------------------------------------
# Juniper.JunOS config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST, deferable
from noc.core.confdb.syntax.patterns import IP_ADDRESS, AS_NUM


class JunOSNormalizer(BaseNormalizer):
    @match("system", "host-name", ANY)
    @match("groups", ANY, "system", "host-name", ANY)
    def normalize_hostname(self, tokens):
        if tokens[0] == "groups":
            yield self.make_hostname(hostname=tokens[4])
        else:
            yield self.make_hostname(hostname=tokens[2])

    @match("system", "domain-name", ANY)
    def normalize_domain_name(self, tokens):
        yield self.make_domain_name(domain_name=tokens[2])

    @match("system", "services", "http")
    def normalize_http_server(self, tokens):
        yield self.make_protocols_http()

    @match("system", "services", "https")
    def normalize_https_server(self, tokens):
        yield self.make_protocols_https()

    @match("system", "login", "user", ANY, "class", ANY)
    def normalize_username_access_level(self, tokens):
        yield self.make_user_class(username=tokens[3], class_name="level-%s" % tokens[5])

    @match("vlans", ANY, "vlan-id", ANY)
    def normalize_vlan_name(self, tokens):
        if tokens[3] != "none":
            yield self.make_vlan_name(vlan_id=tokens[3], name=tokens[1])

    # @match("vlans", ANY, "description", REST)
    # def normalize_vlan_description(self, tokens):
    #     yield self.make_vlan_description(
    #         vlan_id=tokens[1],
    #         description=" ".join(tokens[3:])
    #     )

    @match("interfaces", ANY)
    def normalize_interface(self, tokens):
        if_name = self.interface_name(tokens[1])
        yield self.make_interface(interface=self.interface_name(if_name))
        yield self.make_switchport_untagged(interface=if_name, unit=if_name, vlan_filter=1)

    @match("interfaces", ANY, "description", REST)
    def normalize_interface_description(self, tokens):
        yield self.make_interface_description(
            interface=self.interface_name(tokens[1]), description=" ".join(tokens[3:])
        )

    @match("interfaces", ANY, "unit", ANY, "description", REST)
    def normalize_sub_interface_description(self, tokens):
        if_name = "%s.%s" % (self.interface_name(tokens[1]), tokens[3])
        yield self.defer(
            "fi.iface.%s" % self.interface_name(if_name),
            self.make_unit_description,
            instance=deferable("instance"),
            interface=self.interface_name(if_name),
            unit=self.interface_name(if_name),
            description=" ".join(tokens[5:]),
        )

    @match("interfaces", ANY, "unit", ANY, "family", "inet", "address", ANY)
    def normalize_sub_interface_ip(self, tokens):
        if_name = "%s.%s" % (self.interface_name(tokens[1]), tokens[3])
        yield self.defer(
            "fi.iface.%s" % self.interface_name(if_name),
            self.make_unit_inet_address,
            instance=deferable("instance"),
            interface=self.interface_name(if_name),
            unit=self.interface_name(if_name),
            address=self.to_prefix(tokens[7], None),
        )

    @match("routing-instances", ANY, "bridge-domains", ANY, "interface", ANY)
    def normalize_ri_bridge_interface(self, tokens):
        yield self.defer("fi.iface.%s" % self.interface_name(tokens[5]), instance=tokens[1])
        self.rebase(
            (
                "virtual-router",
                "default",
                "forwarding-instance",
                tokens[1],
                "interfaces",
                self.interface_name(tokens[5]),
            ),
            (
                "virtual-router",
                "default",
                "forwarding-instance",
                "default",
                "interfaces",
                self.interface_name(tokens[5]),
            ),
        )

    @match("routing-instances", ANY, "interface", ANY)
    def normalize_interface_routing_instances(self, tokens):
        yield self.defer("fi.iface.%s" % self.interface_name(tokens[3]), instance=tokens[1])

    @match("routing-instances", ANY, "route-distinguisher", ANY)
    def normalize_routing_instances_rd(self, tokens):
        yield self.make_forwarding_instance_rd(instance=tokens[1], rd=tokens[3])

    @match("routing-instances", ANY, "instance-type", ANY)
    def make_routing_instances_type(self, tokens):
        vrf_type = tokens[3]
        if tokens[3] == "virtual-router":
            vrf_type = "vrf"
        elif tokens[3] == "virtual-switch":
            vrf_type = "bridge"
        yield self.make_forwarding_instance_type(instance=tokens[1], type=vrf_type)

    @match("routing-instances", ANY, "vrf-target", ANY)
    def normalize_routing_instances_rt(self, tokens):
        vrf_taget = tokens[3]
        if vrf_taget.startswith("target"):
            # vrf-target target:10.10.10.10:1010;
            vrf_taget = tokens[3][7:]
        elif vrf_taget.startswith("t:"):
            # vrf-target t:10.10.10.10:1010;
            vrf_taget = tokens[3][2:]
        yield self.make_forwarding_instance_export_target(instance=tokens[1], target=vrf_taget)
        yield self.make_forwarding_instance_import_target(instance=tokens[1], target=vrf_taget)

    @match("routing-instances", ANY, "vrf-target", "export", ANY)
    def normalize_routing_instances_rt_export(self, tokens):
        yield self.make_forwarding_instance_export_target(instance=tokens[1], target=tokens[4][7:])

    @match("routing-instances", ANY, "vrf-target", "import", ANY)
    def normalize_routing_instances_rt_import(self, tokens):
        yield self.make_forwarding_instance_import_target(instance=tokens[1], target=tokens[4][7:])

    @match("routing-instances", ANY, "description", REST)
    def normalize_routing_instances_description(self, tokens):
        yield self.make_forwarding_instance_description(
            instance=tokens[1], description=" ".join(tokens[3:])
        )

    @match("system", "ntp")
    def normalize_timesource(self, tokens):
        yield self.make_clock_source(source="ntp")

    @match("system", "ntp", "server", ANY)
    @match("system", "ntp", "server", ANY, ANY)
    @match("system", "ntp", "server", ANY, ANY, ANY, ANY, ANY)
    def normalize_ntp_server(self, tokens):
        yield self.make_ntp_server_address(name=tokens[3], address=tokens[3])

    @match("system", "name-server", IP_ADDRESS)
    def normalize_dns_name_server(self, tokens):
        yield self.make_protocols_dns_name_server(ip=tokens[2])

    @match("system", "domain-search", ANY)
    def normalize_dns_name_server_search_suffix(self, tokens):
        yield self.make_protocols_dns_search_suffix(suffix=tokens[2])

    @match("system", "tacplus-server")
    def normalize_tacacs_type(self, tokens):
        yield self.make_aaa_service_type(name="tacacs", type="tacacs+")

    @match("system", "authentication-order", ANY)
    def normalize_aaa_service_order(self, tokens):
        service = "tacacs" if tokens[-1] == "tacplus" else tokens[-1]
        yield self.make_aaa_service_order(name=service)

    @match("system", "tacplus-server", IP_ADDRESS)
    def normalize_aaa_tacacs_address(self, tokens):
        yield self.make_aaa_service_address(name="tacacs", ip=tokens[-1])

    @match("system", "tacplus-server", IP_ADDRESS, "source-address", IP_ADDRESS)
    def normalize_aaa_tacacs_source_address(self, tokens):
        yield self.make_aaa_service_address_source(
            name="tacacs", ip=tokens[2], source_ip=tokens[-1]
        )

    @match("system", "tacplus-server", IP_ADDRESS, "secret", ANY)
    def normalize_aaa_tacacs_secret(self, tokens):
        yield self.make_aaa_service_address_tacacs_secret(
            name="tacacs", ip=tokens[2], secret=tokens[-1].strip('"')
        )

    @match("system", "syslog", "host", IP_ADDRESS)
    def normalize_protocols_syslog_server(self, tokens):
        yield self.make_protocols_syslog_server(ip=tokens[3])

    @match("system", "syslog", "host", IP_ADDRESS, "source-address", IP_ADDRESS)
    def normalize_protocols_syslog_server_source(self, tokens):
        yield self.make_protocols_syslog_server_source(ip=tokens[3], source_ip=tokens[5])

    @match("routing-instances", ANY, "protocols", "bgp", "group", ANY, "neighbor", IP_ADDRESS)
    def normalize_bgp_peer_neighbor(self, tokens):
        yield self.make_bgp_neighbor(instance=tokens[1], neighbor=tokens[7])
        yield self.make_bgp_neighbor_peer_group(
            instance=tokens[1], neighbor=tokens[7], group=tokens[5]
        )
        yield self.make_bgp_neighbor_description(
            instance=tokens[1], neighbor=tokens[7], description=tokens[5]
        )
        yield self.defer(
            f"bgp.connection.{tokens[5]}.export_filter",
            self.make_bgp_neighbor_export_filter,
            instance=tokens[1],
            neighbor=tokens[7],
            name=deferable("name"),
        )
        yield self.defer(
            f"bgp.connection.{tokens[5]}.import_filter",
            self.make_bgp_neighbor_import_filter,
            instance=tokens[1],
            neighbor=tokens[7],
            name=deferable("name"),
        )
        yield self.defer(
            f"bgp.connection.{tokens[5]}",
            self.make_bgp_neighbor_type,
            instance=tokens[1],
            neighbor=tokens[7],
            type=deferable("role"),
        )
        yield self.defer(
            f"bgp.routing_options.as",
            self.make_bgp_neighbor_local_as,
            instance=tokens[1],
            neighbor=tokens[7],
            as_num=deferable("as_num"),
        )
        yield self.defer(
            f"bgp.connection.{tokens[5]}",
            self.make_bgp_neighbor_local_address,
            instance=tokens[1],
            neighbor=tokens[7],
            address=deferable("local_address"),
        )

    @match(
        "routing-instances",
        ANY,
        "protocols",
        "bgp",
        "group",
        ANY,
        "neighbor",
        IP_ADDRESS,
        "peer-as",
        AS_NUM,
    )
    def normalize_bgp_peer_as(self, tokens):
        yield self.make_bgp_neighbor_remote_as(
            instance=tokens[1], neighbor=tokens[7], as_num=tokens[9].split(".")[0]
        )

    @match(
        "routing-instances",
        ANY,
        "protocols",
        "bgp",
        "group",
        ANY,
        "neighbor",
        IP_ADDRESS,
        "shutdown",
    )
    def normalize_bgp_peer_admin_status(self, tokens):
        yield self.make_bgp_neighbor_admin_status(
            instance=tokens[1], neighbor=tokens[7], admin_status=False
        )

    @match(
        "routing-instances",
        ANY,
        "protocols",
        "bgp",
        "group",
        ANY,
        "type",
        ANY,
    )
    def normalize_bgp_peer_type(self, tokens):
        yield self.defer(
            f"bgp.connection.{tokens[5]}",
            role=tokens[7],
        )

    @match(
        "routing-instances",
        ANY,
        "protocols",
        "bgp",
        "group",
        ANY,
        "local-address",
        ANY,
    )
    def normalize_bgp_peer_local_address(self, tokens):
        yield self.defer(
            f"bgp.connection.{tokens[5]}",
            local_address=tokens[7],
        )

    @match(
        "routing-instances",
        ANY,
        "protocols",
        "bgp",
        "group",
        ANY,
        "export",
        ANY,
    )
    def normalize_bgp_peer_out_filter(self, tokens):
        yield self.defer(
            f"bgp.connection.{tokens[5]}.export_filter",
            name=tokens[7],
        )

    @match(
        "routing-instances",
        ANY,
        "protocols",
        "bgp",
        "group",
        ANY,
        "import",
        ANY,
    )
    def normalize_bgp_peer_in_filter(self, tokens):
        yield self.defer(
            f"bgp.connection.{tokens[5]}.import_filter",
            name=tokens[7],
        )

    @match("routing-options", "autonomous-system", ANY, "asdot-notation")
    def normalize_router_instances_as(self, tokens):
        yield self.defer(
            f"bgp.routing_options.as",
            as_num=tokens[2],
        )
