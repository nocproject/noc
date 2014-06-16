//---------------------------------------------------------------------
// sa.managedobjectprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobjectprofile.Application");

Ext.define("NOC.sa.managedobjectprofile.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.sa.managedobjectprofile.Model",
        "NOC.main.style.LookupField",
        "NOC.main.ref.stencil.LookupField",
        "Ext.ux.form.MultiIntervalField"
    ],
    model: "NOC.sa.managedobjectprofile.Model",
    search: true,
    rowClassField: "row_class",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Ping",
            dataIndex: "enable_ping",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Config",
            dataIndex: "enable_config_polling",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Version",
            dataIndex: "enable_version_inventory",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Int.",
            dataIndex: "enable_interface_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Asset",
            dataIndex: "enable_asset_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "IP",
            dataIndex: "enable_ip_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Prefix",
            dataIndex: "enable_prefix_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "VLAN",
            dataIndex: "enable_vlan_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "MAC",
            dataIndex: "enable_mac_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "ID",
            dataIndex: "enable_id_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "LLDP",
            dataIndex: "enable_lldp_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "CDP",
            dataIndex: "enable_cdp_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "STP",
            dataIndex: "enable_stp_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "REP",
            dataIndex: "enable_rep_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "BFD",
            dataIndex: "enable_bfd_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "UDLD",
            dataIndex: "enable_udld_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "OAM",
            dataIndex: "enable_oam_discovery",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "IPAM",
            dataIndex: "sync_ipam",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Objects",
            dataIndex: "mo_count",
            width: 50,
            align: "right"
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "Name",
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "style",
            xtype: "main.style.LookupField",
            fieldLabel: "Style",
            allowBlank: true
        },
        {
            name: "shape",
            xtype: "main.ref.stencil.LookupField",
            fieldLabel: "Shape",
            allowBlank: true
        },
        {
            name: "name_template",
            xtype: "textfield",
            fieldLabel: "Name template",
            allowBlank: true
        },
        {
            name: "sync_ipam",
            xtype: "checkboxfield",
            boxLabel: "Enable IPAM synchronization",
            allowBlank: false
        },
        {
            name: "fqdn_template",
            xtype: "textarea",
            fieldLabel: "FQDN template",
            allowBlank: true
        },
        {
            xtype: "fieldcontainer",
            fieldLabel: "Ping Check",
            layout: "hbox",
            items: [
                {
                    name: "enable_ping",
                    xtype: "checkboxfield",
                    fieldLabel: "Enable",
                    allowBlank: false
                },
                {
                    name: "ping_interval",
                    xtype: "numberfield",
                    fieldLabel: "Interval"
                }
            ]
        },
        {
            name: "down_severity",
            xtype: "numberfield",
            fieldLabel: "Down severity",
            allowBlank: false
        },
        {
            name: "check_link_interval",
            xtype: "multiintervalfield",
            fieldLabel: "check_link interval",
            allowBlank: true
        },
        {
            xtype: "fieldcontainer",
            fieldLabel: "Discovery",
            layout: {
                type: "table",
                columns: 4
            },
            items: [
                // Header
                {
                    xtype: "label"
                },
                {
                    xtype: "label",
                    text: "Enabled"
                },
                {
                    xtype: "label",
                    text: "Min. interval"
                },
                {
                    xtype: "label",
                    text: "Max. interval"
                },
                // Config
                {
                    xtype: "label",
                    text: "Config"
                },
                {
                    name: "enable_config_polling",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "config_polling_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "config_polling_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // Version inventory
                {
                    xtype: "label",
                    text: "Version inventory"
                },
                {
                    name: "enable_version_inventory",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "version_inventory_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "version_inventory_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // Interface discovery
                {
                    xtype: "label",
                    text: "Interface discovery"
                },
                {
                    name: "enable_interface_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "interface_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "interface_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // Asset discovery
                {
                    xtype: "label",
                    text: "Asset discovery"
                },
                {
                    name: "enable_asset_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "asset_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "asset_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // IP discovery
                {
                    xtype: "label",
                    text: "IP discovery"
                },
                {
                    name: "enable_ip_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "ip_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "ip_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // Prefix discovery
                {
                    xtype: "label",
                    text: "Prefix discovery"
                },
                {
                    name: "enable_prefix_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "prefix_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "prefix_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // VLAN discovery
                {
                    xtype: "label",
                    text: "VLAN discovery"
                },
                {
                    name: "enable_vlan_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "vlan_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "vlan_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // MAC discovery
                {
                    xtype: "label",
                    text: "MAC discovery"
                },
                {
                    name: "enable_mac_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "mac_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "mac_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // ID
                {
                    xtype: "label",
                    text: "ID discovery"
                },
                {
                    name: "enable_id_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "id_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "id_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // LLDP
                {
                    xtype: "label",
                    text: "LLDP discovery"
                },
                {
                    name: "enable_lldp_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "lldp_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "lldp_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // CDP
                {
                    xtype: "label",
                    text: "CDP discovery"
                },
                {
                    name: "enable_cdp_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "cdp_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "cdp_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // STP
                {
                    xtype: "label",
                    text: "STP discovery"
                },
                {
                    name: "enable_stp_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "stp_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "stp_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // REP
                {
                    xtype: "label",
                    text: "REP discovery"
                },
                {
                    name: "enable_rep_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "rep_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "rep_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // BFD
                {
                    xtype: "label",
                    text: "BFD discovery"
                },
                {
                    name: "enable_bfd_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "bfd_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "bfd_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // UDLD
                {
                    xtype: "label",
                    text: "UDLD discovery"
                },
                {
                    name: "enable_udld_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "udld_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "udld_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                // UDLD
                {
                    xtype: "label",
                    text: "OAM discovery"
                },
                {
                    name: "enable_oam_discovery",
                    xtype: "checkboxfield",
                    allowBlank: false
                },
                {
                    name: "oam_discovery_min_interval",
                    xtype: "numberfield",
                    allowBlank: false
                },
                {
                    name: "oam_discovery_max_interval",
                    xtype: "numberfield",
                    allowBlank: false
                }
            ]
        }
    ]
});
