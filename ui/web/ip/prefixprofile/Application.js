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
        "NOC.ip.prefixprofile.Model",
        "NOC.main.style.LookupField",
        "NOC.main.template.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.wf.workflow.LookupField"
    ],
    model: "NOC.ip.prefixprofile.Model",
    search: true,
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
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: __("Tags"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
