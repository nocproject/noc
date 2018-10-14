//---------------------------------------------------------------------
// sa.managedobjectprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobjectprofile.Model");

Ext.define("NOC.sa.managedobjectprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/managedobjectprofile/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "level",
            type: "int",
            defaultValue: 25
        },
        {
            name: "style",
            type: "int"
        },
        {
            name: "shape",
            type: "string"
        },
        {
            name: "style__label",
            type: "string",
            persist: false
        },
        {
            name: "name_template",
            type: "string"
        },
        {
            name: "card",
            type: "string",
            defaultValue: "managedobject"
        },
        {
            name: "card_title_template",
            type: "string",
            defaultValue: "{{ object.object_profile.name }}: {{ object.name }}"
        },
        {
            name: "fqdn_suffix",
            type: "string"
        },
        {
            name: "address_resolution_policy",
            type: "string"
        },
        {
            name: "resolver_handler",
            type: "string"
        },
        {
            name: "resolver_handler__label",
            type: "string",
            persist: false
        },
        {
            name: "enable_ping",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "ping_interval",
            type: "int",
            defaultValue: 60
        },
        {
            name: "report_ping_rtt",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "report_ping_attempts",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "ping_policy",
            type: "string",
            defaultValue: "f"
        },
        {
            name: "ping_size",
            type: "int",
            defaultValue: 64
        },
        {
            name: "ping_count",
            type: "int",
            defaultValue: 3
        },
        {
            name: "ping_timeout_ms",
            type: "int",
            defaultValue: 1000
        },
        {
            name: "weight",
            type: "int",
            defaultValue: 0
        },
        {
            name: "enable_box_discovery",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "box_discovery_interval",
            type: "integer",
            defaultValue: 86400
        },
        {
            name: "box_discovery_failed_interval",
            type: "integer",
            defaultValue: 10800
        },
        {
            name: "box_discovery_on_system_start",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "box_discovery_system_start_delay",
            type: "integer",
            defaultValue: 300
        },
        {
            name: "box_discovery_on_config_changed",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "box_discovery_config_changed_delay",
            type: "integer",
            defaultValue: 300
        },
        {
            name: "enable_box_discovery_profile",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_version",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_caps",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_interface",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_vpn_interface",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_vpn_mpls",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_prefix_neighbor",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_prefix_interface",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_address_neighbor",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_address_interface",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_address_management",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_address_dhcp",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_id",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_config",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_asset",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_vlan",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_bfd",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_cdp",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_huawei_ndp",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_mikrotik_ndp",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_fdp",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_lldp",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_oam",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_rep",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_stp",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_udld",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_lacp",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_nri",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_nri_portmap",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_nri_service",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_sla",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_cpe",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_mac",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_metrics",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_hk",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_cpestatus",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "box_discovery_cpestatus_policy",
            type: "string",
            defaultValue: "S"
        },
        {
            name: "box_discovery_alarm_policy",
            type: "string"
        },
        {
            name: "box_discovery_fatal_alarm_weight",
            type: "int"
        },
        {
            name: "box_discovery_alarm_weight",
            type: "int"
        },
        {
            name: "cli_session_policy",
            type: "string"
        },
        {
            name: "cli_privilege_policy",
            type: "string"
        },
        {
            name: "access_preference",
            type: "string"
        },
        {
            name: "enable_periodic_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "periodic_discovery_interval",
            type: "integer",
            defaultValue: 300
        },
        {
            name: "enable_periodic_discovery_uptime",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_periodic_discovery_interface_status",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_periodic_discovery_mac",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_periodic_discovery_metrics",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_periodic_discovery_cpestatus",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "periodic_discovery_cpestatus_policy",
            type: "string",
            defaultValue: "S"
        },
        {
            name: "periodic_discovery_alarm_policy",
            type: "string"
        },
        {
            name: "periodic_discovery_fatal_alarm_weight",
            type: "int"
        },
        {
            name: "periodic_discovery_alarm_weight",
            type: "int"
        },
        {
            name: "clear_links_on_platform_change",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "clear_links_on_serial_change",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "cpe_segment_policy",
            type: "string",
            defaultValue: "C"
        },
        {
            name: "cpe_cooldown",
            type: "int",
            defaultValue: 0
        },
        {
            name: "cpe_profile",
            type: "int"
        },
        {
            name: "box_discovery_telemetry_sample",
            type: "int",
            defaultValue: 0
        },
        {
            name: "periodic_discovery_telemetry_sample",
            type: "int",
            defaultValue: 0
        },
        {
            name: "cpe_profile__label",
            type: "string",
            persist: false
        },
        {
            name: "cpe_auth_profile",
            type: "string"
        },
        {
            name: "cpe_auth_profile__label",
            type: "string",
            persist: false
        },
        {
            name: "mac_collect_all",
            type: "boolean"
        },
        {
            name: "mac_collect_interface_profile",
            type: "boolean"
        },
        {
            name: "mac_collect_management",
            type: "boolean"
        },
        {
            name: "mac_collect_multicast",
            type: "boolean"
        },
        {
            name: "mac_collect_vcfilter",
            type: "boolean"
        },
        {
            name: "autosegmentation_policy",
            type: "string",
            defaultValue: "d"
        },
        {
            name: "autosegmentation_level_limit",
            type: "int",
            defaultValue: 999
        },
        {
            name: "autosegmentation_segment_name",
            type: "string",
            defaultValue: "{{ object.name }}"
        },
        {
            name: "hk_handler",
            type: "string"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        },
        {
            name: "mo_count",
            type: "int",
            persist: false
        },
        {
            name: "metrics",
            type: "auto"
        },
        {
            name: "remote_system",
            type: "string"
        },
        {
            name: "remote_system__label",
            type: "string",
            persist: false
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        },
        {
            name: "escalation_policy",
            type: "string"
        },
        {
            name: "syslog_archive_policy",
            type: "string",
            defaultValue: "D"
        },
        {
            name: "neighbor_cache_ttl",
            type: "int",
            defaultValue: 0
        },
        {
            name: "event_processing_policy",
            type: "string"
        },
        {
            name: "address_profile_interface",
            type: "string"
        },
        {
            name: "address_profile_interface__label",
            type: "string",
            persist: false
        },
        {
            name: "address_profile_management",
            type: "string"
        },
        {
            name: "address_profile_management__label",
            type: "string",
            persist: false
        },
        {
            name: "address_profile_neighbor",
            type: "string"
        },
        {
            name: "address_profile_neighbor__label",
            type: "string",
            persist: false
        },
        {
            name: "address_profile_dhcp",
            type: "string"
        },
        {
            name: "address_profile_dhcp__label",
            type: "string",
            persist: false
        },
        {
            name: "prefix_profile_interface",
            type: "string"
        },
        {
            name: "prefix_profile_interface__label",
            type: "string",
            persist: false
        },
        {
            name: "prefix_profile_neighbor",
            type: "string"
        },
        {
            name: "prefix_profile_neighbor__label",
            type: "string",
            persist: false
        },
        {
            name: "vpn_profile_interface",
            type: "string"
        },
        {
            name: "vpn_profile_interface__label",
            type: "string",
            persist: false
        },
        {
            name: "vpn_profile_mpls",
            type: "string"
        },
        {
            name: "vpn_profile_mpls__label",
            type: "string",
            persist: false
        },
        {
            name: "config_mirror_storage",
            type: "string"
        },
        {
            name: "config_mirror_storage__label",
            type: "string",
            persist: false
        },
        {
            name: "config_mirror_template",
            type: "string"
        },
        {
            name: "config_mirror_template__label",
            type: "string",
            persist: false
        },
        {
            name: "config_mirror_policy",
            type: "string",
            defaultValue: "D"
        },
        {
            name: "config_validation_policy",
            type: "string",
            defaultValue: "C"

        },
        {
            name: "beef_storage",
            type: "string"
        },
        {
            name: "beef_storage__label",
            type: "string",
            persist: false
        },
        {
            name: "beef_path_template",
            type: "string"
        },
        {
            name: "beef_path_template__label",
            type: "string",
            persist: false
        },
        {
            name: "beef_policy",
            type: "string",
            defaultValue: "D"
        }
    ]
});
