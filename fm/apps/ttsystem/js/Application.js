//---------------------------------------------------------------------
// fm.ttsystem application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.ttsystem.Application");

Ext.define("NOC.fm.ttsystem.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.ttsystem.Model"
    ],
    model: "NOC.fm.ttsystem.Model",
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
                    text: "Handler",
                    dataIndex: "handler",
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
                    name: "handler",
                    xtype: "textfield",
                    fieldLabel: "Handler",
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    allowBlank: false
                },
                {
                    name: "connection",
                    xtype: "textfield",
                    fieldLabel: "Connection",
                    allowBlank: false
                }
            ]
        });
        me.callParent();
    }
});
