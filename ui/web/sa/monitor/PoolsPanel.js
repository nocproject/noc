//---------------------------------------------------------------------
// sa.monitor PoolsPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.monitor.PoolsPanel");

Ext.define("NOC.sa.monitor.PoolsPanel", {
    extend: "Ext.panel.Panel",
    uses: [],
    title: "Pools",
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
                    stateId: "sa.monitor-pools-grid",
                    store: me.store,
                    features: [{
                        ftype: "groupingsummary",
                        groupHeaderTpl: "Pool: {name}"
                    }],
                    columns: [
                        {
                            text: __("Instance"),
                            dataIndex: "instance"
                        },
                        {
                            text: __("State"),
                            dataIndex: "state"
                        },
                        {
                            text: __("Changed"),
                            dataIndex: "last_state_change",
                            xtype: "datecolumn",
                            format: "Y-m-d H:i:s"
                        },
                        {
                            text: __("Scripts"),
                            columns: [
                                {
                                    text: __("Current"),
                                    dataIndex: "current_scripts",
                                    summaryType: "sum",
                                    align: "right"
                                },
                                {
                                    text: __("Limit"),
                                    dataIndex: "max_scripts",
                                    summaryType: "sum",
                                    align: "right"
                                },
                                {
                                    text: __("Processed"),
                                    dataIndex: "scripts_processed",
                                    summaryType: "sum",
                                    align: "right"
                                },
                                {
                                    text: __("Failed"),
                                    dataIndex: "scripts_failed",
                                    summaryType: "sum",
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
                }
            ]
        });
        me.callParent();
    }
});
