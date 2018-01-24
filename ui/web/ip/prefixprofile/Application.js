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
        "NOC.ip.prefixprofile.LookupField",
        "NOC.main.style.LookupField",
        "NOC.main.remotesystem.LookupField"
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
                    name: "enable_prefix_discovery",
                    xtype: "checkbox",
                    boxLabel: __("Prefix Discovery")
                },
                {
                    name: "autocreated_prefix_profile",
                    xtype: "ip.prefixprofile.LookupField",
                    fieldLabel: __("Discovered Prefix Profile")
                },
                {
                    name: "enable_ip_discovery",
                    xtype: "checkbox",
                    boxLabel: __("IP Discovery")
                },
                {
                    name: "enable_ip_ping_discovery",
                    xtype: "checkbox",
                    boxLabel: __("IP Discovery (Ping)")
                },
                {
                    name: "style",
                    xtype: "main.style.LookupField",
                    fieldLabel: __("Style"),
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
