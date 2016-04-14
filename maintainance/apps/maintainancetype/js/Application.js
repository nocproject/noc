//---------------------------------------------------------------------
// maintainance.maintainancetype application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintainance.maintainancetype.Application");

Ext.define("NOC.maintainance.maintainancetype.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.maintainance.maintainancetype.Model"
    ],
    model: "NOC.maintainance.maintainancetype.Model",
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
                    text: "Suppress",
                    dataIndex: "suppress_alarms",
                    width: 75,
                    renderer: NOC.render.Bool
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
                    uiStyle: "medium",
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    uiStyle: "extra",
                    allowBlank: true
                },
                {
                    name: "suppress_alarms",
                    xtype: "checkbox",
                    boxLabel: "Suppress Alarms"
                }
            ]
        });
        me.callParent();
    }
});
