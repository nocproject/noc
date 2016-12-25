//---------------------------------------------------------------------
// phone.phonenumberprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.phonenumberprofile.Application");

Ext.define("NOC.phone.phonenumberprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.phone.phonenumberprofile.Model"
    ],
    model: "NOC.phone.phonenumberprofile.Model",
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
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
