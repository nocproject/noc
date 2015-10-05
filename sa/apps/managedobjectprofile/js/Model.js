//---------------------------------------------------------------------
// sa.managedobjectprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
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
            name: "fqdn_template",
            type: "string"
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
            name: "down_severity",
            type: "int",
            defaultValue: 4000
        },
        {
            name: "check_link_interval",
            type: "string"
        },
        {
            name: "enable_config_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "config_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "config_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_version_inventory",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "version_inventory_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "version_inventory_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_caps_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "caps_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "caps_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_uptime_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "uptime_discovery_min_interval",
            type: "int",
            defaultValue: 60
        },
        {
            name: "uptime_discovery_max_interval",
            type: "int",
            defaultValue: 300
        },
        {
            name: "enable_interface_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "interface_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "interface_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_interface_status_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "interface_status_discovery_min_interval",
            type: "int",
            defaultValue: 60
        },
        {
            name: "interface_status_discovery_max_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "enable_ip_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "ip_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "ip_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_prefix_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "prefix_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "prefix_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_vlan_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "vlan_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "vlan_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_mac_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "mac_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "mac_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_id_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "id_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "id_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_lldp_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "lldp_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "lldp_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_cdp_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "cdp_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "cdp_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_stp_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "stp_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "stp_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_rep_discovery",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "rep_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "rep_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_bfd_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "bfd_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "bfd_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_udld_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "udld_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "udld_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_oam_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "oam_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "oam_discovery_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_asset_discovery",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "asset_discovery_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "asset_discovery_max_interval",
            type: "int",
            defaultValue: 86400
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
        }
    ]
});
