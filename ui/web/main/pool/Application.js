//---------------------------------------------------------------------
// main.pool application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pool.Application");

Ext.define("NOC.main.pool.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.pool.Model"
    ],
    model: "NOC.main.pool.Model",
    search: true,
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 100
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
                    regex: /^[0-9a-zA-z]{1,16}$/,
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
