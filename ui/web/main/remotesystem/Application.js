//---------------------------------------------------------------------
// main.remotesystem application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.remotesystem.Application");

Ext.define("NOC.main.remotesystem.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.remotesystem.Model"
    ],
    model: "NOC.main.remotesystem.Model",
    search: true,

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
                            name: "enable_service",
                            xtype: "checkbox",
                            boxLabel: __("Service")
                        },
                        {
                            name: "enable_subscriber",
                            xtype: "checkbox",
                            boxLabel: __("Subscriber")
                        },
                        {
                            name: "enable_terminationgroup",
                            xtype: "checkbox",
                            boxLabel: __("Termination Group")
                        },
                        {
                            name: "enable_ttsystem",
                            xtype: "checkbox",
                            boxLabel: __("TT System")
                        },
                        {
                            name: "enable_ttmap",
                            xtype: "checkbox",
                            boxLabel: __("TT Map")
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
