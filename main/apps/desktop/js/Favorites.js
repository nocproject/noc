//---------------------------------------------------------------------
// Favorites panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.Favorites");

Ext.define("NOC.main.desktop.Favorites", {
    extend: "Ext.Panel",
    title: "Favorites",
    iconCls: "icon_star",

    initComponent: function() {
        var me = this;
        me.store = Ext.create("Ext.data.Store", {
            fields: ["app", "title", "launch_info"],
            data: []
        });
        me.grid = Ext.create("Ext.grid.Panel", {
            columns: [
                {
                    xtype: "actioncolumn",
                    width: 20,
                    items: [
                        {
                            iconCls: "icon_star",
                            scope: me
                        }
                    ]
                },
                {
                    dataIndex: "title",
                    flex: 1
                }
            ],
            hideHeaders: true,
            store: me.store,
            listeners: {
                scope: me,
                itemclick: me.onClick
            }
        });
        Ext.apply(me, {
            items: [me.grid]
        });
        me.callParent();
    },
    //
    afterRender: function() {
        var me = this;
        me.callParent();
        me.loadStore();
    },
    // Load data to store
    loadStore: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/main/desktop/favapps/",
            scope: me,
            success: function(result) {
                var me = this,
                    data = Ext.decode(result.responseText);
                me.store.loadData(data);
            }
        });
    },
    // Favorite app clicked
    onClick: function(grid, record, item) {
        var me = this,
            li = record.get("launch_info");
        NOC.run(li.class, li.title, li.params);
    }
});
