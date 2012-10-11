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
        "NOC.main.style.LookupField"
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
            renderer: NOC.render.Bool
        },
        {
            text: "Config",
            dataIndex: "enable_config_polling",
            renderer: NOC.render.Bool
        },
        {
            text: "Version",
            dataIndex: "enable_version_inventory",
            renderer: NOC.render.Bool
        },
        {
            text: "Int.",
            dataIndex: "enable_interface_discovery",
            renderer: NOC.render.Bool
        },
        {
            text: "IP",
            dataIndex: "enable_ip_discovery",
            renderer: NOC.render.Bool
        },
        {
            text: "Prefix",
            dataIndex: "enable_prefix_discovery",
            renderer: NOC.render.Bool
        },
        {
            text: "MAC",
            dataIndex: "enable_mac_discovery",
            renderer: NOC.render.Bool
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
            name: "name_template",
            xtype: "textfield",
            fieldLabel: "Name template",
            allowBlank: true
        },
        {
            name: "enable_ping",
            xtype: "checkboxfield",
            boxLabel: "Enable ping check",
            allowBlank: false
        },
        {
            name: "down_severity",
            xtype: "numberfield",
            fieldLabel: "Down severity",
            allowBlank: false
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
                }
            ]
        }
    ]
});
