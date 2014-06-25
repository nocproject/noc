//---------------------------------------------------------------------
// Tabbed workplace
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.WorkplacePanel");

Ext.define("NOC.main.desktop.WorkplacePanel", {
    extend: "Ext.TabPanel",
    id: "workplace",
    region: "center", // Always required for border layout
    activeTab: 0,
    border: false,
    layout: "fit",
    items: [],
    app: null,
    //
    initComponent: function() {
        var me = this;

        me.expandButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.expand,
            tooltip: "Collapse panels",
            scope: me,
            handler: me.onExpand
        });
        Ext.apply(me, {
            tabBar: {
                items: [
                    {
                        xtype: "tbfill"
                    },
                    me.expandButton
                ]
            },
            listeners: {
                scope: me,
                tabchange: me.onTabChange,
                afterrender: me.onAfterRender
            }
        });
        me.callParent();
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
        if(tab.menu_node) {
            me.app.onCloseApp(tab.menuNode);
        }
        // Run application's onCloseApp
        var app = tab.items.first();
        if(app && Ext.isFunction(app.onCloseApp)) {
            app.onCloseApp();
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
        me.expandButton.setTooltip("Expand panels");
    },
    //
    setCollapsed: function() {
        var me = this;
        me.expandButton.setGlyph(NOC.glyph.expand);
        me.expandButton.setTooltip("Collapse panels");
    }

});
