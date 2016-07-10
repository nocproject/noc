//---------------------------------------------------------------------
// inv.firmware application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.firmware.Application");

Ext.define("NOC.inv.firmware.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.firmware.Model"
    ],
    model: "NOC.inv.firmware.Model",
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
                    text: "Vendor",
                    dataIndex: "vendor",
                    width: 100
                },
                {
                    text: "Version",
                    dataIndex: "version",
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
                    name: "vendor",
                    xtype: "textfield",
                    fieldLabel: "Vendor",
                    allowBlank: false
                },
                {
                    name: "version",
                    xtype: "textfield",
                    fieldLabel: "Version",
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    allowBlank: true
                },
                {
                    name: "download_url",
                    xtype: "textfield",
                    fieldLabel: "URL",
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
