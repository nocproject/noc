//---------------------------------------------------------------------
// pm.metricsettings application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricsettings.Application");

Ext.define("NOC.pm.metricsettings.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.metricsettings.Model"
    ],
    model: "NOC.pm.metricsettings.Model",
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
