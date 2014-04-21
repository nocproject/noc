//---------------------------------------------------------------------
// sa.terminationgroup application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.terminationgroup.Application");

Ext.define("NOC.sa.terminationgroup.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.terminationgroup.Model"
    ],
    model: "NOC.sa.terminationgroup.Model",
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
