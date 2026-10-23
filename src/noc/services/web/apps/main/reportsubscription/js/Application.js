//---------------------------------------------------------------------
// main.reportsubscription application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.reportsubscription.Application");

Ext.define("NOC.main.reportsubscription.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.reportsubscription.Model"
    ],
    model: "NOC.main.reportsubscription.Model",
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
