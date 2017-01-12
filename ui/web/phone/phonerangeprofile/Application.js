//---------------------------------------------------------------------
// phone.phonerangeprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.phonerangeprofile.Application");

Ext.define("NOC.phone.phonerangeprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.phone.phonerangeprofile.Model",
        "NOC.main.style.LookupField"
    ],
    model: "NOC.phone.phonerangeprofile.Model",
    search: true,
    rowClassField: "row_class",

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
                    name: "cooldown",
                    xtype: "numberfield",
                    fieldLabel: __("Cooldown"),
                    uiStyle: "small",
                    minValue: 0,
                    maxValue: 9999,
                    allowBlank: false
                },
                {
                    name: "style",
                    xtype: "main.style.LookupField",
                    fieldLabel: __("Style"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
