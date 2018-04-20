//---------------------------------------------------------------------
// sa.monitor ScriptsPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.monitor.ScriptsPanel");

Ext.define("NOC.sa.monitor.ScriptsPanel", {
    extend: "Ext.panel.Panel",
    uses: [],
    title: "Scripts",
    closable: false,
    layout: "fit",

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            items: [
                {
                    xtype: "gridpanel",
                    border: false,
                    autoScroll: true,
                    stateful: true,
                    stateId: "sa.monitor-Scripts-grid",
                    store: me.store,
                    features: [{
                        ftype: "grouping",
                        groupHeaderTpl: "Pool: {name}"
                    }],
                    columns: [
                        {
                            text: "Instance",
                            dataIndex: "instance"
                        },
                        {
                            text: "Script",
                            dataIndex: "script"
                        },
                        {
                            text: "Object",
                            dataIndex: "object_name"
                        },
                        {
                            text: "Address",
                            dataIndex: "address"
                        },
                        {
                            text: "Start",
                            dataIndex: "start_time",
                            xtype: "datecolumn",
                            format: "Y-m-d H:i:s"
                        },
                        {
                            text: "Timeout",
                            dataIndex: "timeout",
                            align: "right"
                        },
                        {
                            text: "Duration",
                            dataIndex: "duration",
                            align: "right"
                        }
                    ]
                }
            ],
            tbar: [
                {
                    text: "Refresh",
                    glyph: NOC.glyph.refresh,
                    scope: me.app,
                    handler: me.app.refreshData
                }
            ]
        });
        me.callParent();
    }
});
