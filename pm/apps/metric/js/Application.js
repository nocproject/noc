//---------------------------------------------------------------------
// pm.metric application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metric.Application");

Ext.define("NOC.pm.metric.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.metric.Model"
    ],
    model: "NOC.pm.metric.Model",
    search: true,
    changeTitle: null,

    initComponent: function() {
        var me = this;

        me.graph = Ext.create("NOC.core.Graph", {
            timeRange: 3600,
            refreshInterval: 60
        });
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
                    xtype: "displayfield",
                    fieldLabel: "Name"
                },
                me.graph
            ]
        });
        me.callParent();
    },
    //
    showForm: function() {
        var me = this;
        me.callParent();
        if(me.currentRecord) {
            me.graph.setSeries([
                {
                    name: me.currentRecord.get("name")
                }
            ]);
        } else {
            me.graph.setSeries([]);
        }
    }
});
