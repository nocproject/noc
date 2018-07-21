//---------------------------------------------------------------------
// main.apikey application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.apikey.Application");

Ext.define("NOC.main.apikey.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.apikey.Model"
    ],
    model: "NOC.main.apikey.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                }, {
                    text: __("Active"),
                    dataIndex: "is_active",
                    width: 25,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Expires"),
                    dataIndex: "expires",
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
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: __("Active")
                }, /*
                {
                    name: "expires"
                }, */
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "key",
                    xtype: "textfield",
                    fieldLabel: __("API Key"),
                    inputType: "password",
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "access",
                    xtype: "gridfield",
                    fieldLabel: __("Access"),
                    columns: [
                        {
                            text: __("API"),
                            dataIndex: "api",
                            width: 150,
                            editor: "textfield"
                        },
                        {
                            text: __("Role"),
                            dataIndex: "role",
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
