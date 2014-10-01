//---------------------------------------------------------------------
// main.sync application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.sync.Application");

Ext.define("NOC.main.sync.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.sync.Model",
        "NOC.main.user.LookupField"
    ],
    model: "NOC.main.sync.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: "Active",
                    dataIndex: "is_active",
                    renderer: NOC.render.Bool,
                    width: 50
                },
                {
                    text: "Instances",
                    dataIndex: "n_instances",
                    width: 70,
                    align: "right"
                },
                {
                    text: "Credentials",
                    dataIndex: "user",
                    width: 100,
                    renderer: NOC.render.Lookup("user")
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
                    allowBlank: false,
                    fieldLabel: "Name",
                    regex: /^[0-9a-zA-Z\-_\.]+$/
                },
                {
                    name: "is_active",
                    xtype: "checkboxfield",
                    boxLabel: "Active"
                },
                {
                    name: "user",
                    xtype: "main.user.LookupField",
                    fieldLabel: "Credentials"
                },
                {
                    name: "n_instances",
                    xtype: "numberfield",
                    fieldLabel: "Instances",
                    minValue: 1
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    allowBlank: true
                }
            ],
            filters: [
                {
                    title: "Active",
                    name: "is_active",
                    ftype: "boolean"
                }
            ]
        });
        me.callParent();
    }
});
