//---------------------------------------------------------------------
// main.messageroute application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.messageroute.Application");

Ext.define("NOC.main.messageroute.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.ListFormField",
        "NOC.main.messageroute.Model",
        "NOC.main.ref.messagetype.LookupField",
        "NOC.main.ref.messageheader.LookupField",
        "NOC.main.notificationgroup.LookupField",
        "NOC.main.template.LookupField",
        "NOC.main.handler.LookupField"
    ],
    model: "NOC.main.messageroute.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Type"),
                    dataIndex: "type",
                    width: 150
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
                    uiStyle: "medium",
                    allowBlank: false
                },

                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: __("Active")
                },

                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    uiStyle: "extra",
                    allowBlank: true
                },
                {
                    name: "order",
                    xtype: "numberfield",
                    fieldLabel: __("Order"),
                    uiStyle: "small",
                    allowBlank: false
                },
                {
                    name: "type",
                    xtype: "main.ref.messagetype.LookupField",
                    fieldLabel: __("Type"),
                    allowBlank: false
                },
                {
                    name: "match",
                    xtype: "gridfield",
                    fieldLabel: __("Match"),
                    columns: [
                        {
                            text: __("Header"),
                            dataIndex: "header",
                            editor: "main.ref.messageheader.LookupField",
                            width: 250
                        },
                        {
                            text: __("Operation"),
                            dataIndex: "op",
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["==", "=="],
                                    ["!=", "!="],
                                    ["regex", "regex"]
                                ]
                            },
                            width: 100
                        },
                        {
                            text: __("Value"),
                            dataIndex: "value",
                            editor: "textfield",
                            flex: 1
                        }
                    ]
                },
                {
                    name: "transmute",
                    xtype: "listform",
                    fieldLabel: __("Transmute"),
                    items: [
                        {
                            name: "type",
                            xtype: "combobox",
                            store: [
                                ["template", "template"],
                                ["handler", "handler"],
                            ]
                        },
                        {
                            name: "template",
                            xtype: "main.template.LookupField",
                            fieldLabel: __("Template")
                        },
                        {
                            name: "handler",
                            xtype: "main.handler.LookupField",
                            fieldLabel: __("Hanlder"),
                            query: {
                                allow_mx_transmutation: true
                            }
                        }
                    ]
                },
                {
                    name: "action",
                    xtype: "listform",
                    fieldLabel: __("Action"),
                    items: [
                        {
                            name: "type",
                            xtype: "combobox",
                            store: [
                                ["drop", "drop"],
                                ["stream", "stream"],
                                ["notification", "notificaiton"]
                            ],
                            fieldLabel: __("Type"),
                            uiStyle: "medium"
                        },
                        {
                            name: "stream",
                            xtype: "textfield",
                            fieldLabel: __("Stream"),
                            uiStyle: "medium"
                        },
                        {
                            name: "notification_group",
                            xtype: "main.notificationgroup.LookupField",
                            fieldLabel: __("Notification Group")
                        },
                        {
                            name: "headers",
                            xtype: "gridfield",
                            fieldLabel: __("Headers"),
                            columns: [
                                {
                                    text: __("Header"),
                                    dataIndex: "header",
                                    width: 200,
                                    editor: "main.ref.messageheader.LookupField"
                                },
                                {
                                    text: __("Value"),
                                    dataIndex: "value",
                                    flex: 1,
                                    editor: "textfield"
                                }
                            ]
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },
    filters: [
        {
            title: __("Type"),
            name: "type",
            ftype: "lookup",
            lookup: "main.ref.messagetype"
        }
    ]
});