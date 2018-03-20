//---------------------------------------------------------------------
// main.handler application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.handler.Application");

Ext.define("NOC.main.handler.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.handler.Model"
    ],
    model: "NOC.main.handler.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Handler"),
                    dataIndex: "handler",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "meduim"
                },
                {
                    name: "handler",
                    xtype: "textfield",
                    fieldLabel: __("Handler"),
                    allowBlank: false,
                    vtype: "handler",
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "allow_config_filter",
                    xtype: "checkbox",
                    boxLabel: __("Allow Config Filter")
                },
                {
                    name: "allow_config_validation",
                    xtype: "checkbox",
                    boxLabel: __("Allow Config Validation")
                }
            ]
        });
        me.callParent();
    }
});
