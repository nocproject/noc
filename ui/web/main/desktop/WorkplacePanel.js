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
  tabBar: {
    cls: "noc-navigation-header",
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
    Ext.apply(me, {
      listeners: {
        scope: me,
        tabchange: me.onTabChange,
        afterrender: Ext.emptyFn,
      },
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
    Ext.Loader.require(panel_class, function(){
      var app = Ext.create(panel_class, {
        noc: params,
        title: title,
        closable: true,
      });
      var tab = this.add({
        title: title,
        closable: true,
        layout: "fit",
        items: app,
        listeners: {
          scope: this,
          beforeclose: this.onTabClose,
        },
        menuNode: node,
      });
      // Close Home tab, if any
      var first = this.items.first();
      if(first && first.title !== title && first.title === "Home"){
        first.close();
      }
      //
      this.setActiveTab(tab);
      if(node){
        this.up().launchedTabs[node] = tab;
      }
      this.unmask();
    }, this);
  },
  //
  onTabChange: function(panel, tab){
    var app = tab.items.first(),
      h = app.getHistoryHash();
    if(h !== "main.welcome"){
      Ext.History.setHash(h);
    }
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
        homeTab = Ext.Array.findBy(me.workplacePanel.getRefItems(), function(tab){ return tab.items.first().appId === "main.home" });
      if(Ext.isEmpty(homeTab)){
        me.launchTab("NOC.main.home.Application", "Home", {});
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
