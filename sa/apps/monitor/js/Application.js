//---------------------------------------------------------------------
// sa.monitor application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.monitor.Application");

Ext.define("NOC.sa.monitor.Application", {
    extend: "NOC.core.Application",
    uses: [],

    initComponent: function() {
        var me = this;

        me.poolsStore = Ext.create("NOC.sa.monitor.PoolsStore");
        me.scriptsStore = Ext.create("NOC.sa.monitor.ScriptsStore");
        Ext.apply(me, {
            items: [
                Ext.create("Ext.tab.Panel", {
                    border: false,
                    activeTab: 0,
                    layout: "fit",
                    autoScroll: true,
                    items: [
                        Ext.create("NOC.sa.monitor.PoolsPanel", {
                            store: me.poolsStore,
                            app: me
                        }),
                        Ext.create("NOC.sa.monitor.ScriptsPanel", {
                            store: me.scriptsStore,
                            app: me
                        })
                    ]
                })
            ]
        });
        me.callParent();
    },

    afterRender: function() {
        var me = this;

        me.callParent();
        me.refreshData();
    },

    // Run get_activator_info task
    refreshData: function() {
        var me = this;

        NOC.mrt({
            url: "/sa/monitor/mrt/get_activator_info/",
            selector: "SAE",
            loadMask: me,
            scope: me,
            success: me.updateData
        });
    },
    // Upload data to stores
    updateData: function(result) {
        var me = this,
            poolsData = [],
            scriptsData = [];
        if(!result[0].status) {
            NOC.error("Failed to get data");
            return;
        }
        Ext.each(result[0].result, function(r) {
            poolsData.push({
                pool:r.pool,
                instance: r.instance,
                state: r.state,
                last_state_change: new Date(r.last_state_change * 1000),
                current_scripts: r.current_scripts,
                max_scripts: r.max_scripts,
                scripts_processed: r.scripts_processed,
                scripts_failed: r.scripts_failed
            });
            Ext.each(r.scripts, function(rr) {
                scriptsData.push({
                    pool: r.pool,
                    instance: r.instance,
                    object_name: rr.object_name,
                    script: rr.script,
                    address: rr.address,
                    start_time: new Date(rr.start_time * 1000),
                    duration: r.timestamp - rr.start_time,
                    timeout: rr.timeout
                });
            })
        });
        me.poolsStore.loadData(poolsData);
        me.scriptsStore.loadData(scriptsData);
        console.log(result);
    }
});
