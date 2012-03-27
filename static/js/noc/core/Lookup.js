//---------------------------------------------------------------------
// NOC.core.Lookup -
// Simple lookup Store with id and label fields
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Lookup");

Ext.define("NOC.core.Lookup", {
    extend: "Ext.data.Store",
    fields: ["id", "label"],
    url: null,
    //autoLoad: true,
    constructor: function(config) {
        var me = this;
        Ext.apply(me, {
            proxy: Ext.create("Ext.data.RestProxy", {
                url: me.url,
                pageParam: "__page",
                startParam: "__start",
                limitParam: "__limit",
                sortParam: "__sort",
                extraParams: {
                    "__format": "ext"
                },
                reader: {
                    type: "json",
                    root: "data",
                    totalProperty: "total",
                    successProperty: "success"
                }
                })
        });
        me.callParent(config);
    }
});