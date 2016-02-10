//---------------------------------------------------------------------
// Subscribers plugin
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.plugins.Subscribers");

Ext.define("NOC.fm.alarm.plugins.Subscribers", {
    extend: "Ext.panel.Panel",
    title: "Subscribers",
    app: null,
    autoScroll: true,
    bodyPadding: 4,

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            fields: [
                "interface", "profile", "description"
            ],
            data: []
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            autoScroll: true,
            store: me.store,
            columns: [
                {
                    dataIndex: "interface",
                    text: "Interface",
                    width: 150
                },
                {
                    dataIndex: "profile",
                    text: "Profile",
                    width: 150
                },
                {
                    dataIndex: "description",
                    text: "Description",
                    flex: 1
                }
            ]
        });

        Ext.apply(me, {
            items: [
                me.grid
            ]
        });

        me.callParent();
    },

    updateData: function(data) {
        var me = this;
        me.store.loadData(data.subscribers);
    }
});
