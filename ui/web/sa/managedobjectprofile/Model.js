//---------------------------------------------------------------------
// sa.managedobjectprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
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
            name: "shape_overlay_glyph",
            type: "string"
        },
        {
            name: "shape_overlay_glyph__label",
            type: "string",
            persist: false
        },
        {
            name: "shape_overlay_position",
            type: "string"
        },
        {
            name: "shape_overlay_form",
            type: "string"
        },
        {
            name: "shape_title_template",
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
            type: "string",
            defaultValue: "D"
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
            name: "new_platform_creation_policy",
            type: "string",
            defaultValue: "C"
        },
        {
            name: "denied_firmware_policy",
            type: "string",
            defaultValue: "I"
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
            name: "ping_time_expr_policy",
            type: "string",
            defaultValue: "D"
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
            name: "box_discovery_running_policy",
            type: "string",
            defaultValue: "R"
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
            name: "enable_box_discovery_bgppeer",
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
            name: "enable_box_discovery_vpn_confdb",
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
            name: "enable_box_discovery_prefix_confdb",
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
            name: "enable_box_discovery_address_confdb",
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
            name: "enable_box_discovery_ifdesc",
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
            name: "mac_collect_vlanfilter",
            type: "string",
        },
        {
            name: "enable_box_discovery_xmac",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_hk",
            type: "boolean",
            defaultValue: false
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
        },
        {
            name: "periodic_discovery_running_policy",
            type: "string",
            defaultValue: "R"
        },
        {
            name: "enable_periodic_discovery_uptime",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "periodic_discovery_uptime_interval",
            type: "integer",
            defaultValue: 0
        },
        {
            name: "enable_periodic_discovery_interface_status",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "periodic_discovery_interface_status_interval",
            type: "integer",
            defaultValue: 0
        },
        {
            name: "enable_periodic_discovery_mac",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "periodic_discovery_mac_interval",
            type: "integer",
            defaultValue: 0
        },
        {
            name: "periodic_discovery_mac_filter_policy",
            type: "string",
            defaultValue: "A"
        },
        {
            name: "enable_periodic_discovery_alarms",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "periodic_discovery_alarms_interval",
            type: "integer",
            defaultValue: 0
        },
        {
            name: "enable_periodic_discovery_cpestatus",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "periodic_discovery_cpestatus_interval",
            type: "integer",
            defaultValue: 0
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
            name: "enable_periodic_discovery_peerstatus",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "periodic_discovery_peerstatus_interval",
            type: "integer",
            defaultValue: 0
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
            name: "caps_profile",
            type: "string"
        },
        {
            name: "caps_profile__label",
            type: "string",
            persist: false
        },
        {
            name: "bgppeer_profile",
            type: "string"
        },
        {
            name: "bgppeer_profile__label",
            type: "string",
            persist: false
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
            name: "hk_handler__label",
            type: "string",
            persist: false
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
            name: "enable_metrics",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "metrics_default_interval",
            type: "integer",
            defaultValue: 300
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
            name: "address_profile_confdb",
            type: "string"
        },
        {
            name: "address_profile_confdb__label",
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
            name: "prefix_profile_confdb",
            type: "string"
        },
        {
            name: "prefix_profile_confdb__label",
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
            name: "vpn_profile_confdb",
            type: "string"
        },
        {
            name: "vpn_profile_confdb__label",
            type: "string",
            persist: false
        },
        {
            name: "vlan_interface_discovery",
            type: "string",
            defaultValue: "D"
        },
        {
            name: "vlan_vlandb_discovery",
            type: "string",
            defaultValue: "D"
        },
        {
            name: "config_download_storage",
            type: "string"
        },
        {
            name: "config_download_storage__label",
            type: "string",
            persist: false
        },
        {
            name: "config_download_template",
            type: "string"
        },
        {
            name: "config_download_template__label",
            type: "string",
            persist: false
        },
        {
            name: "config_policy",
            type: "string",
            defaultValue: "s"
        },
        {
            name: "config_fetch_policy",
            type: "string",
            defaultValue: "r"
        },
        {
            name: "interface_discovery_policy",
            type: "string",
            defaultValue: "s"
        },
        {
            name: "caps_discovery_policy",
            type: "string",
            defaultValue: "s"
        },
        {
            name: "vlan_discovery_policy",
            type: "string",
            defaultValue: "s"
        },
        {
            name: "bgpeer_discovery_policy",
            type: "string",
            defaultValue: "c"
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
            name: "confdb_raw_policy",
            type: "string",
            defaultValue: "D"

        },
        {
            name: "dynamic_classification_policy",
            type: "string",
            defaultValue: "R"
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
        },
        {
            name: "workflow",
            type: "string"
        },
        {
            name: "workflow__label",
            type: "string",
            persist: false
        },
        {
            name: "object_validation_policy",
            type: "string"
        },
        {
            name: "object_validation_policy__label",
            type: "string",
            persist: false
        },
        {
            name: "ifdesc_patterns",
            type: "string"
        },
        {
            name: "ifdesc_patterns__label",
            type: "string",
            persist: false
        },
        {
            name: "ifdesc_handler",
            type: "string"
        },
        {
            name: "ifdesc_handler__label",
            type: "string",
            persist: false
        },
        {
            name: "ifdesc_symmetric",
            type: "boolean"
        },
        {
            name: "enable_rca_downlink_merge",
            type: "boolean"
        },
        {
            name: "rca_downlink_merge_window",
            type: "integer",
            defaultValue: 120
        },
        {
            name: "enable_interface_autocreation",
            type: "boolean"
        },
        {
            name: "snmp_rate_limit",
            type: "int",
            defaultValue: 0
        },
        {
            name: "abduct_detection_window",
            type: "integer",
            defaultValue: 0
        },
        {
            name: "abduct_detection_threshold",
            type: "integer",
            defaultValue: 0
        },
        {
            name: "trapcollector_storm_policy",
            type: "string",
            defaultValue: "D"
        },
        {
            name: "trapcollector_storm_threshold",
            type: "int",
            defaultValue: 1000
        },
        {
            name: "labels",
            type: "auto"
        },
        {
            name: "match_rules",
            type: "auto"
        }
    ]
});
