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
                            text: "Instance",
                            dataIndex: "instance"
                        },
                        {
                            text: "State",
                            dataIndex: "state"
                        },
                        {
                            text: "Changed",
                            dataIndex: "last_state_change",
                            xtype: "datecolumn",
                            format: "Y-m-d H:i:s"
                        },
                        {
                            text: "Scripts",
                            columns: [
                                {
                                    text: "Current",
                                    dataIndex: "current_scripts",
                                    summaryType: "sum",
                                    align: "right"
                                },
                                {
                                    text: "Limit",
                                    dataIndex: "max_scripts",
                                    summaryType: "sum",
                                    align: "right"
                                },
                                {
                                    text: "Processed",
                                    dataIndex: "scripts_processed",
                                    summaryType: "sum",
                                    align: "right"
                                },
                                {
                                    text: "Failed",
                                    dataIndex: "scripts_failed",
                                    summaryType: "sum",
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
                }
            ]
        });
        me.callParent();
    }
});
