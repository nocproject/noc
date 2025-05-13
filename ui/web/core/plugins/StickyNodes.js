//---------------------------------------------------------------------
// NOC.core.plugins StickyNodes for TreePanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.plugins.StickyNodes");

Ext.define("NOC.core.plugins.StickyNodes", {
  extend: "Ext.plugin.Abstract",
  alias: "plugin.stickynodesview",
    
  zIndex: 100,
  stickyCls: "sticky-node",
  rowHeight: 36, // for noc theme
  config: {
    enabled: true,
  },
    
  init: function(treePanel){
    this.tree = treePanel;
    this.observerMap = new Map(); // node -> {level, internalId}
    this.stickyNodes = new Map(); // level -> {node, observer} - объединяем информацию о прилипших узлах и их наблюдателях
    this.view = treePanel.getView();
    this.store = treePanel.getStore();
      
    this.tree.on("viewready", this.setupGlobalObserver, this);
    this.tree.on("afteritemcollapse", this.refreshObservers, this);
    this.tree.on("afteritemexpand", this.refreshObservers, this);
    this.tree.on("beforedestroy", this.destroy, this);
    // ToDO: check resize
    // this.view.on("afterlayout", this.refreshObservers, this);
    // this.tree.on("afterlayout", this.refreshObservers, this);
   
    this.createStickyCss(1)
  },
  //
  setupGlobalObserver: function(){
    this.globalObserver = new IntersectionObserver(this.handleIntersect.bind(this), {
      root: this.view.getEl().dom,
      rootMargin: "0px 0px 0px 0px",
      threshold: [0, 1],
    });
    console.log("Global IntersectionObserver created");
    Ext.fly(this.view.getEl().dom).down(".x-grid-item-container").setStyle("overflow", "unset");
    var nodes = this.view.getNodes(1);
    if(nodes.length > 0){
      this.rowHeight = Ext.fly(nodes[0]).getHeight();
    }
    this.initIntersectionObservers();
  },
  //
  refreshObservers: function(record, index, item){
    var nodes = this.view.getNodes(index + 1, index + record.childNodes.length);
    // update sticky current node ONLY
    Ext.fly(item).addCls(`${this.stickyCls}-${record.get("depth")}`);
    console.log("Refreshing observers before", this.observerMap.size);
    for(const node of nodes){
      this.addIntersectionObserver(node);
    }

    // Очистка от "мертвых" элементов (удалённых из DOM)
    for(const [node] of this.observerMap){
      if(!document.body.contains(node)){
        this.globalObserver.unobserve(node);
        this.observerMap.delete(node);
      }
    }
    console.log("Refreshing observers after", this.observerMap.size);
  },
  //
  initIntersectionObservers: function(){
    for(const node of this.view.getNodes()){
      this.addIntersectionObserver(node);         
    }
  },
  //
  addIntersectionObserver: function(node){
    if(this.observerMap.has(node)) return;
    var record = this.store.getByInternalId(node.dataset.recordid);
    if(!Ext.isEmpty(record)){
    // if(!Ext.isEmpty(record) && !record.get("leaf")){
      var level = parseInt(record.get("depth"), 10);
      this.globalObserver.observe(node);
      this.observerMap.set(node, {internalId: record.internalId, level});
      Ext.fly(node).addCls(this.stickyCls + "-" + level);
      if(!this.isStickyCssExist(node)){
        this.createStickyCss(level);
      }
      console.log("Adding sticky class to node", level, node);
    }
  },
  //
  destroy: function(){
    for(const node of this.observerMap.keys()){
      this.globalObserver.unobserve(node);
    }
    this.globalObserver.disconnect();
    this.observerMap.clear();
  },
  //
  handleIntersect: function(entries){
    console.log("handleIntersect :", entries.length);
    for(const entry of entries){
      const record = this.view.getRecord(entry.target);
      if(!record) continue;
      // 
      const isAboveTop = entry.boundingClientRect.top < entry.rootBounds.top;
      console.log("Intersecting : ", record.get("name"), isAboveTop);
      if(!entry.isIntersecting && isAboveTop){
      // Строка ушла вверх
        console.log("leave-top", record.get("name"));
      } else if(entry.isIntersecting && isAboveTop){
      // Строка вернулась сверху
        console.log("enter-top", record.get("name"));
      }
    }
  },
  //
  createStickyCss: function(level){
    var css = `.${this.stickyCls}-${level} { position: sticky; top: ${(level -1) * this.rowHeight}px; z-index: ${this.zIndex}; }`;
    Ext.util.CSS.createStyleSheet(css);
  },
  //
  isStickyCssExist: function(node){
    return window.getComputedStyle(node).position === "sticky";
  },
});
