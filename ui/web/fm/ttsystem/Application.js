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
                    text: __("Name"),
                    dataIndex: "name",
                    width: 100
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
                    allowBlank: false
                },
                {
                    name: "handler",
                    xtype: "textfield",
                    fieldLabel: __("Handler"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "connection",
                    xtype: "textfield",
                    fieldLabel: __("Connection"),
                    allowBlank: false
                },
                {
                    name: "failure_cooldown",
                    xtype: "numberfield",
                    fieldLabel: __("Failure Cooldown"),
                    allowBlank: true,
                    min: 0,
                    uiStyle: "small"
                }
            ]
        });
        me.callParent();
    }
});
