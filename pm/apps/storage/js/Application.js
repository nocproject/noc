//---------------------------------------------------------------------
// pm.storage application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.storage.Application");

Ext.define("NOC.pm.storage.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.storage.Model"
    ],
    model: "NOC.pm.storage.Model",
    search: true,
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: "Type",
                    dataIndex: "type",
                    width: 75
                },
                {
                    text: "Description",
                    dataIndex: "description",
                    flex: 1
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
                    name: "type",
                    xtype: "combobox",
                    fieldLabel: "Type",
                    allowBlank: false,
                    store: [
                        ["whisper", "Whisper"],
                        ["ceres", "Ceres"]
                    ]
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description"
                },
                {
                    name: "collectors",
                    xtype: "gridfield",
                    fieldLabel: "Collectors",
                    columns: [
                        {
                            text: "Protocol",
                            dataIndex: "protocol",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["line", "line"]
                                ]
                            }
                        },
                        {
                            text: "Active",
                            dataIndex: "is_active",
                            width: 50,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        },
                        {
                            text: "Address",
                            dataIndex: "address",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: "Port",
                            dataIndex: "port",
                            width: 75,
                            editor: "numberfield"
                        }
                    ]
                },
                {
                    name: "access",
                    xtype: "gridfield",
                    fieldLabel: "Access",
                    columns: [
                        {
                            text: "Protocol",
                            dataIndex: "protocol",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["graphite", "graphite"]
                                ]
                            }
                        },
                        {
                            text: "Active",
                            dataIndex: "is_active",
                            width: 50,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        },
                        {
                            text: "Base URL",
                            dataIndex: "base_url",
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
