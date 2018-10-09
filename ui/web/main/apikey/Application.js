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
        "NOC.main.apikey.Model",
        "NOC.core.PasswordGenerator"
    ],
    model: "NOC.main.apikey.Model",
    search: true,
    helpId: "reference-apikey",

    initComponent: function() {
        var me = this;
        me.keyField = Ext.create({
            name: "key",
            xtype: "password",
            fieldLabel: __("API Key"),
            allowBlank: false,
            margin: "0 5 0 0",
            maxLength: 24,
            maxLengthText: __("The maximum length for this field is {0}"),
            minWidth: 390,
            uiStyle: "large"
        });
        me.keyGenerator = Ext.create("NOC.core.PasswordGenerator");
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
                    xtype: "container",
                    layout: {
                        type: "hbox",
                        align: "center"
                    },
                    margin: "0 0 5",
                    items: [
                        me.keyField,
                        {
                            xtype: "button",
                            padding: "0 15 0 15",
                            text: __("Generate key"),
                            scope: me,
                            handler: me.generateKey
                        }
                    ]
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
    },
    generateKey: function() {
        var me = this;
        me.keyField.setValue(me.keyGenerator.generate(24));
    }
});
