//---------------------------------------------------------------------
// Navigation panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
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
  maxStickyLevel: 1,
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
      tbar: [{
        xtype: "searchfield",
        itemId: "filter",
        width: "100%",
        emptyText: __("Search"),
        scope: this,
        handler: this.onSearch,
        minChars: 2,
        typeAheadDelay: 100,
        triggers: {
          clear: {
            cls: "x-form-clear-trigger",
            hidden: true,
            scope: this,
            handler: this.onClearSearch,
          },
        },
      }],
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
        afterrender: function(){
          me.store.on("datachanged", me._calculateRowHeight, me);
          me.store.on("rootchange", me._calculateRowHeight, me);
        },
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
    var uniqueId = "nav-panel-" + Ext.id();
    
    treePanel.addCls(uniqueId);
    Ext.util.CSS.createStyleSheet(
      `.${uniqueId} .x-grid-item-container { overflow: unset !important; }`,
    );
  },
  //
  _calculateRowHeight: function(){
    var nodes,
      view = this.getView();
    Ext.defer(function(){
      nodes = view.getNodes(0, 0);
      if(Ext.isDefined(nodes.length) && nodes.length > 0){
        this.rowHeight = Ext.fly(nodes[0]).getHeight();
        if(this.maxStickyLevel > 0){
          for(var i = 1; i <= this.maxStickyLevel; i++){
            this.createStickyCss(i);
          }
        } else{
          this.createStickyCss(1);
        }
      } else{
        Ext.defer(this._calculateRowHeight, 100, this);
      }
    }, 100, this);
  },
  //
  createStickyCss: function(level){
    var css = `table.x-grid-item:has(tr.${this.stickyNode}-${level}) { position: sticky; top: ${(level - 1) * this.rowHeight}px; z-index: ${this.zIndex}; }`;
    Ext.util.CSS.createStyleSheet(css);
    this.maxStickyLevel = level;
  },
  //
  onClearSearch: function(field){
    field.setValue("");
    field.getTrigger("clear").hide();
    this.clearSearch();
  },
  //
  onSearch: function(query){
    var matchedNodes = [],
      visibleNodeIds = {},
      field = this.down("[itemId=filter]");
 
    if(this.searchTimer){
      clearTimeout(this.searchTimer);
      this.searchTimer = null;
    }
    
    if(Ext.isEmpty(query)){
      field.getTrigger("clear").hide();
    } else{
      field.getTrigger("clear").show();
    }
    if(Ext.isEmpty(query) || query.length < field.minChars){
      this.clearSearch();
      return;
    }
    
    query = query.toLowerCase();
    
    this.store.getRootNode().cascadeBy(function(record){
      var name = record.get("text") || "";
      if(name.toLowerCase().indexOf(query) !== -1 && record.isLeaf()){
        matchedNodes.push(record);        
        visibleNodeIds[record.getId()] = true;
        var parent = record.parentNode;
        while(parent && !parent.isRoot()){
          visibleNodeIds[parent.getId()] = true;
          parent = parent.parentNode;
        }
      }
    });
    this.store.clearFilter();
    this.store.filterBy(function(record){
      return visibleNodeIds[record.getId()] === true;
    });
    this.searchTimer = Ext.defer(function(){
      for(const node of matchedNodes){
        let parent = node.parentNode;
        while(parent && !parent.isRoot()){
          parent = parent.parentNode;
        }
      }
      if(this.store && this.store.getRootNode() && this.store.getRootNode().hasChildNodes()){
        this.expandAll();
      }
    }, 300, this);
    if(matchedNodes.length < 1){
      NOC.info(__("No matches found"));
    }
  },
  //
  clearSearch: function(){
    if(this.searchTimer){
      clearTimeout(this.searchTimer);
      this.searchTimer = null;
    }
  
    this.store.clearFilter();
    this.searchTimer = Ext.defer(function(){
      if(this.store && this.store.getRootNode() && this.store.getRootNode().hasChildNodes()){
        this.collapseAll();
      }
    }, 300, this);
  },
  
  onDestroy: function(){
    if(this.searchTimer){
      clearTimeout(this.searchTimer);
      this.searchTimer = null;
    }
    this.callParent();
  },
});
