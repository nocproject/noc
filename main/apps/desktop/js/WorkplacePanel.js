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
    // Launch application in tab
    launch_tab: function(panel_class, title, params) {
        var tab = this.add({
            title: title,
            closable: true,
            autoScroll: true,
            layout: "fit",
            items: [Ext.create(panel_class, {"noc": params})]
        });
        this.setActiveTab(tab);
        tab.on("beforeclose", function(tab) {
            if(tab.menu_node && tab.desktop_controller)
                tab.desktop_controller.on_close_tab(tab.menu_node);
        });
        return tab;
    }
});
