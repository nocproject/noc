//---------------------------------------------------------------------
// cm.validationpolicysettings application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.validationpolicysettings.Application");

Ext.define("NOC.cm.validationpolicysettings.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.cm.validationpolicysettings.Model"
    ],
    model: "NOC.cm.validationpolicysettings.Model",
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
