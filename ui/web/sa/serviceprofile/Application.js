//---------------------------------------------------------------------
// sa.serviceprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.serviceprofile.Application");

Ext.define("NOC.sa.serviceprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.LabelField",
        "NOC.sa.serviceprofile.Model",
        "NOC.main.ref.glyph.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.inv.interfaceprofile.LookupField",
        "NOC.inv.capability.LookupField"
    ],
    model: "NOC.sa.serviceprofile.Model",
    search: true,
    helpId: "reference-service-profile",

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            columns: [
                {
                    text: __("Icon"),
                    dataIndex: "glyph",
                    width: 25,
                    renderer: function(v) {
                        if(v !== undefined && v !== "")
                        {
                            return "<i class='" + v + "'></i>";
                        } else {
                            return "";
                        }
                    }
                },
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Code"),
                    dataIndex: "code",
                    width: 100
                },
                {
                    text: __("Summary"),
                    dataIndex: "show_in_summary",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true,
                    uiStyle: "extra"
                },
                {
                    name: "code",
                    xtype: "textfield",
                    fieldLabel: __("Code"),
                    allowBlank: true,
                    uiStyle: "medium"
                },
                {
                    name: "card_title_template",
                    xtype: "textfield",
                    fieldLabel: __("Title Template"),
                    uiStyle: "extra",
                    allowBlank: true
                },
                {
                    name: "glyph",
                    xtype: "main.ref.glyph.LookupField",
                    fieldLabel: __("Icon"),
                    allowBlank: true,
                    uiStyle: "large"
                },
                {
                    name: "display_order",
                    xtype: "numberfield",
                    fieldLabel: __("Display Order"),
                    uiStyle: "small",
                    minValue: 0,
                    allowBlank: false
                },
                {
                    name: "show_in_summary",
                    xtype: "checkbox",
                    boxLabel: __("Show in summary"),
                    allowBlank: true
                },
                {
                    name: "interface_profile",
                    xtype: "inv.interfaceprofile.LookupField",
                    fieldLabel: __("Interface Profile"),
                    allowBlank: true
                },
                {
                    name: "weight",
                    xtype: "numberfield",
                    fieldLabel: __("Alarm weight"),
                    allowBlank: true,
                    uiStyle: "small"
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
                    uiStyle: "extra",
                    query: {
                        "enable_serviceprofile": true
                    }
                },
                {
                    name: "caps",
                    xtype: "gridfield",
                    fieldLabel: __("Capabilities"),
                    allowBlank: true,
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "capability",
                            renderer: NOC.render.Lookup("capability"),
                            width: 250,
                            editor: "inv.capability.LookupField"
                        },
                        {
                            text: __("Value"),
                            dataIndex: "value",
                            flex: 1,
                            editor: "textfield"
                        },
                        {
                            text: __("Scope"),
                            dataIndex: "scope",
                            width: 150,
                            editor: "textfield"
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
