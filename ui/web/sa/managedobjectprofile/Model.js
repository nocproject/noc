//---------------------------------------------------------------------
// sa.managedobjectprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
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
            name: "fqdn_template",
            type: "string",
            defaultValue: "{{ object.address }}.example.com"
        },
        {
            name: "sync_ipam",
            type: "boolean",
            defaultValue: false
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
            defautlValue: true
        },
        {
            name: "box_discovery_interval",
            type: "integer",
            defautlValue: 86400
        },
        {
            name: "box_discovery_failed_interval",
            type: "integer",
            defautlValue: 10800
        },
        {
            name: "box_discovery_on_system_start",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "box_discovery_system_start_delay",
            xtype: "integer",
            defaultValue: 300
        },
        {
            name: "box_discovery_on_config_changed",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "box_discovery_config_changed_delay",
            xtype: "integer",
            defaultValue: 300
        },
        {
            name: "enable_box_discovery_profile",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_version",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_caps",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_interface",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_prefix",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_id",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_config",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_asset",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_vlan",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_bfd",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_cdp",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_huawei_ndp",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_mikrotik_ndp",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_fdp",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_lldp",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_oam",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_rep",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_stp",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_udld",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_lacp",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_nri",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_sla",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_cpe",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_mac",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_metrics",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_box_discovery_hk",
            xtype: "boolean",
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
            name: "enable_periodic_discovery",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "periodic_discovery_interval",
            xtype: "integer",
            defaultValue: 300
        },
        {
            name: "enable_periodic_discovery_uptime",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_periodic_discovery_interface_status",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_periodic_discovery_mac",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "enable_periodic_discovery_metrics",
            xtype: "boolean",
            defaultValue: false
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
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "clear_links_on_serial_change",
            xtype: "boolean",
            defaultValue: false
        },
        {
            name: "cpe_segment_policy",
            xtype: "string",
            defaultValue: "C"
        },
        {
            name: "cpe_cooldown",
            xtype: "int",
            defaultValue: 0
        },
        {
            name: "cpe_profile",
            xtype: "int"
        },
        {
            name: "box_discovery_telemetry_sample",
            type: "int"
        },
        {
            name: "periodic_discovery_telemetry_sample",
            type: "int"
        },
        {
            name: "cpe_profile__label",
            xtype: "string",
            persist: false
        },
        {
            name: "cpe_auth_profile",
            xtype: "string"
        },
        {
            name: "cpe_auth_profile__label",
            xtype: "string",
            persist: false
        },
        {
            name: "mac_collect_all",
            xtype: "boolean"
        },
        {
            name: "mac_collect_interface_profile",
            xtype: "boolean"
        },
        {
            name: "mac_collect_management",
            xtype: "boolean"
        },
        {
            name: "mac_collect_multicast",
            xtype: "boolean"
        },
        {
            name: "mac_collect_vcfilter",
            xtype: "boolean"
        },
        {
            name: "hk_handler",
            xtype: "string"
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
        }
    ]
});
