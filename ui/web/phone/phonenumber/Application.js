//---------------------------------------------------------------------
// phone.phonenumber application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.phonenumber.Application");

Ext.define("NOC.phone.phonenumber.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.phone.phonenumber.Model"
    ],
    model: "NOC.phone.phonenumber.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                /*
                {
                    text: "Name",
                    dataIndex: "name"
                }*/
            ],

            fields: [
    ]
        });
        me.callParent();
    }
});
