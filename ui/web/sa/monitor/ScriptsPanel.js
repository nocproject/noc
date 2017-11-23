//---------------------------------------------------------------------
// sa.monitor ScriptsPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.monitor.ScriptsPanel");

Ext.define("NOC.sa.monitor.ScriptsPanel", {
    extend: "Ext.panel.Panel",
    title: __("Scripts"),
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
                            text: __("Instance"),
                            dataIndex: "instance"
                        },
                        {
                            text: __("Script"),
                            dataIndex: "script"
                        },
                        {
                            text: __("Object"),
                            dataIndex: "object_name"
                        },
                        {
                            text: __("Address"),
                            dataIndex: "address"
                        },
                        {
                            text: __("Start"),
                            dataIndex: "start_time",
                            xtype: "datecolumn",
                            format: "Y-m-d H:i:s"
                        },
                        {
                            text: __("Timeout"),
                            dataIndex: "timeout",
                            align: "right"
                        },
                        {
                            text: __("Duration"),
                            dataIndex: "duration",
                            align: "right"
                        }
                    ]
                }
            ],
            tbar: [
                {
                    text: __("Refresh"),
                    glyph: NOC.glyph.refresh,
                    scope: me.app,
                    handler: me.app.refreshData
                }
            ]
        });
        me.callParent();
    }
});
