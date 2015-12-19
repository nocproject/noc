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
})
;
