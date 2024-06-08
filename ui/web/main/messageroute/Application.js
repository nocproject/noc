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
        "NOC.sa.administrativedomain.LookupField",
        "NOC.core.tagfield.Tagfield",
        "NOC.core.label.LabelField",
        "NOC.main.template.LookupField",
        "NOC.main.handler.LookupField"
    ],
    model: "NOC.main.messageroute.Model",
    search: true,
    formMinWidth: 800,
    formMaxWidth: 1000,

    initComponent: function() {
        var me = this,
            fieldSetDefaults = {
                xtype: "container",
                padding: 5,
                layout: "form",
                columnWidth: 0.5
            };
        ;

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    renderer: NOC.render.Bool,
                    width: 50
                },
                {
                    text: __("Type"),
                    dataIndex: "type",
                    width: 150
                },
                {
                    text: __("Order"),
                    dataIndex: "order",
                    width: 50
                },
                {
                    text: __("Action"),
                    dataIndex: "action",
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
                    xtype: "fieldset",
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    border: false,
                    items: [
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
                            labelAlign: "left",
                            allowBlank: false
                        },
                        {
                            name: "telemetry_sample",
                            xtype: "numberfield",
                            fieldLabel: __("Telemetry Sample"),
                            uiStyle: "small",
                            allowBlank: true
                        }]
                },
                {
                    xtype: "fieldset",
                    layout: "column",
                    title: __("Transmute"),
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            name: "transmute_template",
                            xtype: "main.template.LookupField",
                            fieldLabel: __("Template")
                        },
                        {
                            name: "transmute_handler",
                            xtype: "main.handler.LookupField",
                            fieldLabel: __("Hanlder"),
                            query: {
                                allow_mx_transmutation: true
                            }
                        }
                   ]
                },
                {
                    xtype: "fieldset",
                    layout: "column",
                    title: __("Action"),
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: fieldSetDefaults,
                    collapsible: true,
                    items: [
                        {
                            name: "action",
                            xtype: "combobox",
                            store: [
                                ["drop", "Drop"],
                                ["dump", "Dump"],
                                ["stream", "Stream"],
                                ["notification", "Notificaiton"]
                            ],
                            fieldLabel: __("Action"),
                            uiStyle: "medium",
                            allowBlank: false
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
                            name: "render_template",
                            xtype: "main.template.LookupField",
                            fieldLabel: __("Render Template")
                        }
                    ]
                },
                {
                    name: "headers",
                    xtype: "gridfield",
                    fieldLabel: __("Set Headers"),
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
                            editor: {
                                xtype: "textfield",
                                allowBlank: false // Это запретит изменение поля "value" на пустое значение
                            }
                        }
                    ]
                },
                {
                    name: "match",
                    xtype: "listform",
                    fieldLabel: __("Match Rules"),
                    rows: 5,
                    items: [
                        {
                            name: "labels",
                            xtype: "labelfield",
                            fieldLabel: __("Match Labels"),
                            allowBlank: true,
                            isTree: true,
                            pickerPosition: "down",
                            uiStyle: "extra",
                            query: {
                                "allow_matched": true
                            }
                        },
                        {
                            name: "exclude_labels",
                            xtype: "labelfield",
                            fieldLabel: __("Exclude Match Labels"),
                            allowBlank: true,
                            isTree: true,
                            pickerPosition: "down",
                            uiStyle: "extra",
                            query: {
                                "allow_matched": true
                            }
                        },
                        {
                            xtype: "core.tagfield",
                            url: "/inv/resourcegroup/lookup/",
                            fieldLabel: __("Object Groups"),
                            name: "resource_groups"
                        },
                        {
                            name: "administrative_domain",
                            xtype: "sa.administrativedomain.LookupField",
                            fieldLabel: __("Adm. Domain"),
                            allowBlank: true
                        },
                        {
                            name: "headers_match",
                            xtype: "gridfield",
                            fieldLabel: __("Headers Match"),
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