//---------------------------------------------------------------------
// Tabbed workplace
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.WorkplacePanel");

Ext.define("NOC.main.desktop.WorkplacePanel", {
    extend: "Ext.tab.Panel",
    region: "center", // Always required for border layout
    activeTab: 0,
    border: false,
    layout: "fit",
    app: null,
    //
    initComponent: function() {
        var me = this;

        me.expandButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.expand,
            tooltip: __("Collapse panels"),
            enableToggle: true,
            scope: me,
            handler: me.onExpand,
            getActualRotation: function() {return 0;}
        });
        Ext.apply(me, {
            listeners: {
                scope: me,
                tabchange: me.onTabChange,
                afterrender: me.onAfterRender
            }
        });
        me.callParent();
        me.tabBar.add({
            xtype: "tbfill",
            getActualRotation: function() {return 0;}
        });
        me.tabBar.add(me.expandButton);
    },
    // Launch application in tab
    launchTab: function(panel_class, title, params, node) {
        var me = this,
            app = Ext.create(panel_class, {
                noc: params,
                title: title,
                closable: true
            }),
            tab = me.add({
                title: title,
                closable: true,
                layout: "fit",
                items: [app],
                listeners: {
                    scope: me,
                    beforeclose: me.onTabClose
                },
                menuNode: node
            });
        // Close Welcome tab, if any
        var first = me.items.first();
        if(first && first.title != title && first.title == "Welcome") {
            first.close();
        }
        //
        me.setActiveTab(tab);
        return tab;
    },
    //
    onTabChange: function(panel, tab) {
        var me = this,
            app = tab.items.first(),
            h = app.getHistoryHash();
        if(h !== "main.welcome") {
            Ext.History.setHash(h);
        }
    },
    //
    onTabClose: function(tab) {
        var me = this;
        // Run desktop's onCloseApp
        if(tab.menuNode) {
            me.app.onCloseApp(tab.menuNode);
        }
        // Run application's onCloseApp
        var app = tab.items.first();
        if(app && Ext.isFunction(app.onCloseApp)) {
            app.onCloseApp();
        }
        if(me.items.length === 1) {
            // Except *Expand* button
            Ext.History.setHash("");
        }
    },
    // Process history
    onAfterRender: function() {
    },
    //
    onExpand: function() {
        var me = this;
        me.app.onPanelsToggle();
    },
    //
    setExpanded: function() {
        var me = this;
        me.expandButton.setGlyph(NOC.glyph.compress);
        me.expandButton.setTooltip(__("Expand panels"));
    },
    //
    setCollapsed: function() {
        var me = this;
        me.expandButton.setGlyph(NOC.glyph.expand);
        me.expandButton.setTooltip(__("Collapse panels"));
    }

});
