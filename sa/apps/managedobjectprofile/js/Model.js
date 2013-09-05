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
            name: "enable_config_polling",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "config_polling_min_interval",
            type: "int",
            defaultValue: 600
        },
        {
            name: "config_polling_max_interval",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "enable_version_inventory",
            type: "boolean",
            defaultValue: true
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
            name: "enable_interface_discovery",
            type: "boolean",
            defaultValue: true
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
            name: "enable_ip_discovery",
            type: "boolean",
            defaultValue: true
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
            defaultValue: true
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
            defaultValue: true
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
            defaultValue: true
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
            defaultValue: true
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
            defaultValue: true
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
            defaultValue: true
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
            defaultValue: true
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
            defaultValue: true
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
            defaultValue: true
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
