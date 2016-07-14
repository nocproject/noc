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
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Vendor"),
                    dataIndex: "vendor",
                    width: 100
                },
                {
                    text: __("Version"),
                    dataIndex: "version",
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
                    name: "vendor",
                    xtype: "textfield",
                    fieldLabel: __("Vendor"),
                    allowBlank: false
                },
                {
                    name: "version",
                    xtype: "textfield",
                    fieldLabel: __("Version"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "download_url",
                    xtype: "textfield",
                    fieldLabel: __("URL"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
