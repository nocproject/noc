//---------------------------------------------------------------------
// NOC.core.ModelStore
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ModelStore");

Ext.define("NOC.core.ModelStore", {
    extend: "Ext.data.Store",
    filterParams: undefined,

    initComponent: function() {
        var me = this;

        me.addEvents(
            /**
             * Fires on succes load() operation
             */
            "loadsuccess",
            /**
             * Fires on failed load() operation
             */
            "loadfailed"
        );
        me.callParent();
    },

    setFilterParams: function(config) {
        var me = this;
        me.filterParams = Ext.Object.merge({}, config);
        // Forcefully go to first page
        me.currentPage = 1;
    },

    load: function(config) {
        var me = this;
        config = Ext.Object.merge({
                params: Ext.Object.merge({}, me.filterParams)
            }, config);
        // Override callback
        // @todo: Call original callback
        config = Ext.Object.merge(config, {
            callback: function(records, operation, success) {
                if(!success)
                    NOC.error("Failed to fetch data!");
            }
        });
        // Continue loading
        me.callParent([config]);
    }
});
