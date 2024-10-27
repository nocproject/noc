//---------------------------------------------------------------------
// main.remotesystem application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.remotesystem.Application");

Ext.define("NOC.main.remotesystem.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.remotesystem.Model",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.main.remotesystem.Model",
    search: true,
    helpId: "reference-remote-system",

    initComponent: function () {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 100
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
                    name: "bi_id",
                    xtype: "displayfield",
                    fieldLabel: __("BI ID"),
                    allowBlank: true,
                    uiStyle: "medium"
                },
                {
                    name: "handler",
                    xtype: "textfield",
                    fieldLabel: __("Handler"),
                    allowBlank: false,
                    uiStyle: "extra"
                },
                {
                    xtype: "fieldset",
                    title: __("Extractors/Loaders"),
                    items: [
                        {
                            name: "enable_address",
                            xtype: "checkbox",
                            boxLabel: __("Address")
                        },
                        {
                            name: "enable_admdiv",
                            xtype: "checkbox",
                            boxLabel: __("Administrative-Territorial Division")
                        },
                        {
                            name: "enable_administrativedomain",
                            xtype: "checkbox",
                            boxLabel: __("Administrative Domain")
                        },
                        {
                            name: "enable_authprofile",
                            xtype: "checkbox",
                            boxLabel: __("Auth Profile")
                        },
                        {
                            name: "enable_building",
                            xtype: "checkbox",
                            boxLabel: __("Building")
                        },
                        {
                            name: "enable_container",
                            xtype: "checkbox",
                            boxLabel: __("Container")
                        },
                        {
                            name: "enable_link",
                            xtype: "checkbox",
                            boxLabel: __("Link")
                        },
                        {
                            name: "enable_managedobject",
                            xtype: "checkbox",
                            boxLabel: __("Managed Object")
                        },
                        {
                            name: "managed_object_loader_policy",
                            xtype: "combobox",
                            fieldLabel: __("Managed Object Loader Policy"),
                            store: [
                                ["M", __("As Managed Object")],
                                ["D", __("As Discovered")],
                            ],
                            value: "M",
                        },
                        {
                            name: "enable_managedobjectprofile",
                            xtype: "checkbox",
                            boxLabel: __("Managed Object Profile")
                        },
                        {
                            name: "enable_networksegment",
                            xtype: "checkbox",
                            boxLabel: __("Network Segment")
                        },
                        {
                            name: "enable_networksegmentprofile",
                            xtype: "checkbox",
                            boxLabel: __("Network Segment Profile")
                        },
                        {
                            name: "enable_object",
                            xtype: "checkbox",
                            boxLabel: __("Object")
                        },
                        {
                            name: "enable_sensor",
                            xtype: "checkbox",
                            boxLabel: __("Sensor")
                        },
                        {
                            name: "enable_service",
                            xtype: "checkbox",
                            boxLabel: __("Service")
                        },
                        {
                            name: "enable_serviceprofile",
                            xtype: "checkbox",
                            boxLabel: __("Service Profile")
                        },
                        {
                            name: "enable_ipvrf",
                            xtype: "checkbox",
                            boxLabel: __("IP VRF")
                        },
                        {
                            name: "enable_ipprefix",
                            xtype: "checkbox",
                            boxLabel: __("IP Prefix")
                        },
                        {
                            name: "enable_ipprefixprofile",
                            xtype: "checkbox",
                            boxLabel: __("IP Prefix Profile")
                        },
                        {
                            name: "enable_ipaddress",
                            xtype: "checkbox",
                            boxLabel: __("IP Address")
                        },
                        {
                            name: "enable_ipaddressprofile",
                            xtype: "checkbox",
                            boxLabel: __("IP Address Profile")
                        },
                        {
                            name: "enable_street",
                            xtype: "checkbox",
                            boxLabel: __("Street")
                        },
                        {
                            name: "enable_subscriber",
                            xtype: "checkbox",
                            boxLabel: __("Subscriber")
                        },
                        {
                            name: "enable_subscriberprofile",
                            xtype: "checkbox",
                            boxLabel: __("Subscriber Profile")
                        },
                        {
                            name: "enable_resourcegroup",
                            xtype: "checkbox",
                            boxLabel: __("Resource Group")
                        },
                        {
                            name: "enable_l2domain",
                            xtype: "checkbox",
                            boxLabel: __("L2 Domain")
                        },
                        {
                            name: "enable_ttsystem",
                            xtype: "checkbox",
                            boxLabel: __("TT System")
                        },
                        {
                            name: "enable_project",
                            xtype: "checkbox",
                            boxLabel: __("Project")
                        },
                        {
                            name: "enable_label",
                            xtype: "checkbox",
                            boxLabel: __("Labels")
                        },
                        {
                            name: "enable_fmevent",
                            xtype: "checkbox",
                            boxLabel: __("Enable FM Event")
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "vbox",
                    title: __("Sync Settings"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "sync_policy",
                            xtype: "combobox",
                            fieldLabel: __("Sync Policy"),
                            allowBlank: false,
                            labelWidth: 200,
                            queryMode: "local",
                            displayField: "label",
                            valueField: "id",
                            defaultValue: "M",
                            store: {
                                fields: ["id", "label"],
                                data: [
                                    {id: "M", label: "Manual"},
                                    {id: "P", label: "Period"},
                                    {id: "C", label: "Cron"}
                                ]
                            },
                            uiStyle: "medium"
                        },
                        {
                            name: "sync_interval",
                            xtype: "numberfield",
                            fieldLabel: __("Sync Interval, sec"),
                            labelWidth: 200,
                            allowBlank: false,
                            uiStyle: "small",
                            minValue: 0,
                            listeners: {
                                scope: me,
                                change: function(_item, newValue, oldValue, eOpts) {
                                    me.form.findField("sync_interval").setValue(newValue);
                                }
                            }
                        },
                        {
                            name: "event_sync_interval",
                            xtype: "numberfield",
                            fieldLabel: __("Event Sync Interval, sec"),
                            labelWidth: 200,
                            allowBlank: false,
                            uiStyle: "small",
                            minValue: 0,
                            listeners: {
                                scope: me,
                                change: function(_item, newValue, oldValue, eOpts) {
                                    me.form.findField("event_sync_interval").setValue(newValue);
                                }
                            }
                        },
                        {
                            name: "sync_notification",
                            xtype: "combobox",
                            fieldLabel: __("Sync Notification Policy"),
                            allowBlank: false,
                            labelWidth: 200,
                            queryMode: "local",
                            displayField: "label",
                            valueField: "id",
                            defaultValue: "F",
                            store: {
                                fields: ["id", "label"],
                                data: [
                                    {id: "D", label: "Disable"},
                                    {id: "F", label: "Failed Only"},
                                    {id: "A", label: "All"}
                                ]
                            },
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Synd Data"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "last_extract",
                            xtype: "displayfield",
                            fieldLabel: __("Last Extract"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "last_load",
                            xtype: "displayfield",
                            fieldLabel: __("Last Load"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "last_extract_event",
                            xtype: "displayfield",
                            fieldLabel: __("Last Extract Event"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    name: "environment",
                    xtype: "gridfield",
                    fieldLabel: __("Environment"),
                    columns: [
                        {
                            text: __("Key"),
                            dataIndex: "key",
                            width: 200,
                            editor: "textfield"
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
        });
        me.callParent();
    }
});
