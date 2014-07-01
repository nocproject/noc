//---------------------------------------------------------------------
// Navigation tree panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.NavTree");

Ext.define("NOC.main.desktop.NavTree", {
    extend: "Ext.tree.Panel",
    title: "Navigation",
    glyph: NOC.glyph.globe,
    useArrows: true,
    rootVisible: false,
    singleExpand: true,
    app: null,

    initComponent: function() {
        var me = this;
        me.store = Ext.create("NOC.main.desktop.NavTreeStore");
        Ext.apply(me, {
            store: me.store,
            listeners: {
                scope: me,
                itemclick: me.onItemClick
            }
        });
        me.callParent();
    },
    //
    updateMenu: function() {
        var me = this;
        if(!me.store.isLoading()) {
            me.store.load();
        }
    },
    //
    onItemClick: function(view, record, item, index, event, opts) {
        var me = this;
        var reuse = !event.shiftKey;

        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/launch_info/",
            params: {
                node: record.data.id
            },
            scope: this,
            success: function(response, opts) {
                var data = Ext.decode(response.responseText);
                me.app.launchTab(
                    data["class"], data["title"], data["params"], opts.params.node, reuse);
            },
            failure: function() {
                NOC.error("Cannot launch application");
            }
        });
    },

});
