//---------------------------------------------------------------------
// pm.thresholdprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.thresholdprofile.Application");

Ext.define("NOC.pm.thresholdprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.thresholdprofile.Model"
    ],
    model: "NOC.pm.thresholdprofile.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
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
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "umbrella_filter_handler",
                    xtype: "textfield",
                    fieldLabel: __("Umbrella Filter Handler"),
                    allowBlank: true,
                    uiStyle: "large"
                    // vtype: "handler"
                }
            ]
        });
        me.callParent();
    }
});
