//---------------------------------------------------------------------
// ip.prefixprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.prefixprofile.Application");

Ext.define("NOC.ip.prefixprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.ip.prefixprofile.Model",
        "NOC.ip.addressprofile.Model",
        "NOC.inv.resourcepool.LookupField",
        "NOC.main.style.LookupField",
        "NOC.main.template.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.wf.workflow.LookupField"
    ],
    model: "NOC.ip.prefixprofile.Model",
    search: true,
    helpId: "prefix-profile",
    rowClassField: "row_class",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Workflow"),
                    dataIndex: "workflow",
                    width: 100,
                    renderer: NOC.render.Lookup("workflow")
                },
                {
                    text: __("Prefix"),
                    dataIndex: "prefix_discovery_policy",
                    width: 100,
                    renderer: NOC.render.Choices({
                        E: __("Enabled"),
                        D: __("Disabled")
                    })
                },
                {
                    text: __("Address"),
                    dataIndex: "address_discovery_policy",
                    width: 100,
                    renderer: NOC.render.Choices({
                        E: __("Enabled"),
                        D: __("Disabled")
                    })
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    uiStyle: "medium",
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "prefix_discovery_policy",
                    xtype: "combobox",
                    fieldLabel: __("Prefix Discovery"),
                    store: [
                        ["E", "Enable"],
                        ["D", "Disable"]
                    ],
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "address_discovery_policy",
                    xtype: "combobox",
                    fieldLabel: __("Address Discovery"),
                    store: [
                        ["E", "Enable"],
                        ["D", "Disable"]
                    ],
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "enable_ip_ping_discovery",
                    xtype: "checkbox",
                    boxLabel: __("IP Discovery (Ping)")
                },
                {
                    name: "workflow",
                    xtype: "wf.workflow.LookupField",
                    fieldLabel: __("Workflow"),
                    allowBlank: false
                },
                {
                    name: "style",
                    xtype: "main.style.LookupField",
                    fieldLabel: __("Style"),
                    allowBlank: true
                },
                {
                    name: "name_template",
                    xtype: "main.template.LookupField",
                    fieldLabel: __("Template"),
                    allowBlank: true
                },
                {
                    name: "default_address_profile",
                    xtype: "ip.addressprofile.LookupField",
                    fieldLabel: __("Default Address Profile"),
                    allowBlank: true
                },
                {
                    name: "seen_propagation_policy",
                    xtype: "combobox",
                    fieldLabel: __("Seen propagation"),
                    allowBlank: false,
                    store: [
                        ["P", __("Propagate")],
                        ["E", __("Enable")],
                        ["D", __("Disable")]
                    ],
                    uiStyle: "medium"
                },
                {
                    name: "prefix_special_address_policy",
                    xtype: "combobox",
                    tooltip: __("Include special addresses (Network & Broadcast for IPv4) <br/>" +
                                    "in prefix range"),
                    fieldLabel: __("Special addresses"),
                    allowBlank: false,
                    store: [
                        ["I", __("Include")],
                        ["X", __("Exclude")]
                    ],
                    uiStyle: "medium",
                    listeners: {
                        render: me.addTooltip
                    }
                },
                {
                    name: "pools",
                    xtype: "gridfield",
                    fieldLabel: __("Address Pools"),
                    columns: [
                        {
                            text: __("Pool"),
                            dataIndex: "pool",
                            width: 200,
                            editor: {
                                xtype: "inv.resourcepool.LookupField"
                            },
                            renderer: NOC.render.Lookup("pool")
                        },
                        {
                            dataIndex: "description",
                            text: __("Description"),
                            editor: "textfield",
                            width: 150
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "remote_system",
                            xtype: "main.remotesystem.LookupField",
                            fieldLabel: __("Remote System"),
                            allowBlank: true
                        },
                        {
                            name: "remote_id",
                            xtype: "textfield",
                            fieldLabel: __("Remote ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "bi_id",
                            xtype: "displayfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    query: {
                        "enable_prefixprofile": true
                    },
                }
            ]
        });
        me.callParent();
    }
});
