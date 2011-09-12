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
    items: [],
    // Launch application in tab
    launch_tab: function(panel_class, title, params) {
        var tab = this.add({
            title: title,
            closable: true,
            items: [Ext.create(panel_class, {"noc": params})]
        });
        this.setActiveTab(tab);
    }
});
