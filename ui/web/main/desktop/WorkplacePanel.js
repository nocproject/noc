//---------------------------------------------------------------------
// Tabbed workplace
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.WorkplacePanel");

Ext.define("NOC.main.desktop.WorkplacePanel", {
  extend: "Ext.tab.Panel",
  itemId: "workplacePanel",
  region: "center", // Always required for border layout
  activeTab: 0,
  border: false,
  layout: "card", // Ext set layout automatically to card!
  app: null,
  tabBar: {
    cls: "noc-navigation-header",
  },
  listeners: {
    tabchange: "onTabChange",
    afterrender: Ext.emptyFn,
  },
  //
  initComponent: function(){
    var me = this;

    me.expandButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.expand,
      tooltip: __("Collapse panels"),
      enableToggle: true,
      scope: me,
      cls: "noc-navigation-button",
      handler: me.onExpand,
      getActualRotation: function(){return 0;},
    });
    me.callParent();
    me.tabBar.add({
      xtype: "tbfill",
      getActualRotation: function(){return 0;},
    });
    me.tabBar.add(me.expandButton);
  },
  // Launch application in tab
  launchTab: function(panel_class, title, params, node){
    this.mask(__("Loading tab with") + " " + panel_class + " ...");
    var tab = this.add({
        title: title,
        closable: true,
        layout: "fit",
        items: Ext.create(panel_class, {
          noc: params,
          title: title,
          closable: true,
        }),
        listeners: {
          scope: this,
          beforeclose: this.onTabClose,
        },
        menuNode: node,
      }),
      homeApp = this.down("[appId=main.home]");
      // Close Home tab, if any
    if(homeApp){
      var homeTab = homeApp.up();
      if(homeTab && homeTab !== tab){
        homeTab.close();
      }
    }
    //
    this.setActiveTab(tab);
    if(node){
      this.up().launchedTabs[node] = tab;
    }
    this.unmask();
  },
  //
  onTabChange: function(panel, tab){
    var app = tab.items.first(),
      h = app.getHistoryHash();
    Ext.History.setHash(h);
  },
  //
  onTabClose: function(tab){
    // Run desktop's onCloseApp
    if(tab.menuNode){
      this.app.onCloseApp(tab.menuNode);
    }
    // Run application's onCloseApp
    var app = tab.items.first();
    if(app && Ext.isFunction(app.onCloseApp)){
      app.onCloseApp();
    }
    if(this.items.length === 1){
      // Except *Expand* button
      var me = this.up(), // Desktop Application
        homeTab = me.workplacePanel.down("[appId=main.home]");
      if(Ext.isEmpty(homeTab)){
        me.launchTab("NOC.main.home.Application", __("Home"), {});
      } else{
        var tabIndex = me.workplacePanel.items.indexOf(homeTab);
        me.workplacePanel.setActiveTab(tabIndex);
      }
    }
  },
  //
  onExpand: function(){
    var me = this;
    me.app.onPanelsToggle();
  },
  //
  setExpanded: function(){
    var me = this;
    me.expandButton.setGlyph(NOC.glyph.compress);
    me.expandButton.setTooltip(__("Expand panels"));
  },
  //
  setCollapsed: function(){
    var me = this;
    me.expandButton.setGlyph(NOC.glyph.expand);
    me.expandButton.setTooltip(__("Collapse panels"));
  },
});
