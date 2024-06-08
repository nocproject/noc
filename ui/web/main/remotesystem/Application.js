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
                            name: "enable_discoveredobject",
                            xtype: "checkbox",
                            boxLabel: __("Enable Discovered")
                        },
                        {
                            name: "enable_fmevent",
                            xtype: "checkbox",
                            boxLabel: __("Enable FM Event")
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
