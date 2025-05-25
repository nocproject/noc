//---------------------------------------------------------------------
// Navigation panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.NavPanel");

Ext.define("NOC.main.desktop.NavPanel", {
  extend: "Ext.tree.Panel",
  region: "west",
  width: 200,
  animCollapse: true,
  collapseFirst: false,
  split: true,
  layout: "fit",
  app: null,
  useArrows: true,
  rootVisible: false,
  singleExpand: false,
  lines: false,
  hideHeaders: true,
  title: __("Navigation"),
  glyph: NOC.glyph.globe,
  store: null,
  header: {
    cls: "noc-navigation-header",
  },
  rowHeight: 36, // for noc theme
  stickyNode: "nav-sticky-node",
  maxStickyLevel: 0,
  zIndex: 100,
  bufferedRenderer: false,
  //
  viewConfig: {
    getRowClass: function(record){
      var me = this.up("treepanel"),
        depth = parseInt(record.get("depth"), 10),
        isNewLevel = depth > me.maxStickyLevel;
      if(isNewLevel){
        me.createStickyCss(depth);
      }
      return `${me.stickyNode}-${depth}`;
    },
  },
  //
  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      tools: [{
        type: "up",
        tooltip: __("Switch to breadcrumb view"),
        cls: "noc-navigation-tool", 
        listeners: {
          scope: me,
          click: function(){me.app.toggleNav();},
        },
      }],
      listeners: {
        scope: me,
        itemclick: me.onItemClick,
        viewready: me._onViewReady,
      },
    });
    me.callParent();
  },
  //
  onItemClick: function(view, record, item, index, event){
    var me = this;
    me.app.launchRecord(record, !event.shiftKey);
  },
  //
  _onViewReady: function(treePanel){
    var uniqueId = "nav-panel-" + Ext.id(),
      rowForHeight = treePanel.getView().getNodes(0, 0)[0];
    
    if(rowForHeight){
      const root = treePanel.store.getRootNode();
      this.rowHeight = Ext.fly(rowForHeight).getHeight();
      root.eachChild(function(child){
        if(child.get("measurementNode") === true){
          root.removeChild(child);
          return false;
        }
      });
    }
  
    treePanel.addCls(uniqueId);
    Ext.util.CSS.createStyleSheet(
      `.${uniqueId} .x-grid-item-container { overflow: unset !important; }`,
    );
  },
  //
  createStickyCss: function(level){
    var css = `table.x-grid-item:has(tr.${this.stickyNode}-${level}) { position: sticky; top: ${(level - 1) * this.rowHeight}px; z-index: ${this.zIndex}; }`;
    Ext.util.CSS.createStyleSheet(css);
    this.maxStickyLevel = level;
  },
});
