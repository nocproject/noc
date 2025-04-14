//---------------------------------------------------------------------
// NOC.core.Application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Application");

Ext.define("NOC.core.Application", {
  extend: "Ext.panel.Panel",
  layout: "fit",
  permissions: {}, // User permissions
  navTooltipTemplate: undefined,
  themeBodyPadding: 4,

  constructor: function(options){
    var me = this;
    // Initialize templates when exists
    me.appId = me.appId || options.noc.app_id;
    me.templates = NOC.templates[me.appId.replace(".", "_")];
    // Set up permissions before calling initComponent
    me.permissions = {};
    for(var p in options.noc.permissions){
      me.permissions[options.noc.permissions[p]] = true;
    }
    // Fix custom fields regex
    if(options.noc.cust_form_fields){
      Ext.iterate(options.noc.cust_form_fields, function(obj){
        if(obj.regex){
          obj.regex = new RegExp(obj.regex);
        }
      });
    }
    me.appTitle = options.title;
    me.noc = options.noc;
    me._registeredItems = [];
    me.currentHistoryHash = me.appId;
    me.callParent(options);
  },
  //
  initComponent: function(){
    var me = this;
    me.on("afterrender", me.processCommands, me);
    me.callParent();
  },
  //
  hasPermission: function(name){
    return this.permissions[name] === true;
  },
  // Filter items and hide not available
  applyPermissions: function(items){
    var me = this;
    Ext.each(items, function(i){
      if(Ext.isDefined(i.hasAccess) && !i.hasAccess(me)){
        // Hide item
        i.hidden = true;
      }
    });
    return items;
  },
  // Register new item and return id
  registerItem: function(item){
    var me = this,
      items = me._registeredItems;
    if(Ext.isString(item)){
      item = Ext.create(item, {app: me});
    }
    var itemId = items.push(item) - 1;
    me._registeredItems = items;
    return itemId;
  },
  //
  showItem: function(index){
    var me = this;
    if(index === null || index === undefined){
      return undefined;
    }
    me.getLayout().setActiveItem(index);
    return me.items.items[index];
  },
  //
  previewItem: function(index, record){
    var me = this,
      back = me.getLayout().getActiveItem(),
      item = me.showItem(index);
    item.preview(record, back);
    return item;
  },
  //
  getRegisteredItems: function(){
    var me = this;
    return me._registeredItems;
  },
  //
  getRegisteredItem: function(index){
    return this._registeredItems[index];
  },
  //
  getRegisteredItemByUrl: function(suffix){
    var me = this;
    return me._registeredItems.findIndex(function(item){
      return item.urlSuffix === suffix;
    });
  },
  //
  processCommands: function(){
    var me = this,
      cmd = me.getCmd();
    if(cmd){
      var handler = me["onCmd_" + cmd];
      if(Ext.isFunction(me.noc.cmd.callback)){
        me.noc.cmd.callback();
      }
      // Override close handler for sa.managedobject only!
      if(me.appId === "sa.managedobject" && !Ext.isEmpty(me.noc.cmd.override)){
        me.down("[xtype=managedobject.form]").getController().toMain = function(){
          me.up().close();
        }
      }
      if(Ext.isFunction(handler)){
        handler.call(me, me.noc.cmd);
      }
    }
  },
  //
  getHistoryHash: function(){
    var me = this;
    return me.currentHistoryHash;
  },
  //
  setHistoryHash: function(){
    this.currentHistoryHash = [this.appId].concat([].slice.call(arguments, 0)).join("/");
    Ext.History.setHash(this.currentHistoryHash);
    if(arguments.length === 0){
      this.setQueryParam();
    }
  },
  //
  setQueryParam: function(){
    let filterPanel = this.lookup("filterPanel");
    if(Ext.isEmpty(filterPanel)){
      return;
    }
    let filterVm = filterPanel.getViewModel();
    if(Ext.isEmpty(filterVm)){
      return;
    }
    let filter = filterVm.get("filterObject");
    if(Ext.Object.isEmpty(filter)){
      return
    }
    this.getController().saveFilterToUrl(filter);
  },
  //
  onCloseApp: function(){},
  //
  getCmd: function(){
    var me = this;
    return (me.noc.cmd && me.noc.cmd.cmd) ? me.noc.cmd.cmd : null;
  },
  //
  log: function(){
    var me = this,
      msg = [me.$className + ":"];
    for(var i = 0; i < arguments.length; i++){
      msg.push(arguments[i]);
    }
    console.log.apply(console, msg);
  },
  // Check application tab is active
  isActiveApp: function(){
    var me = this;
    return me.ownerCt.isVisible();
  },
  //
  setNavTabTooltip: function(ctx){
    var me = this,
      txt;
    if(!me.navTooltipTemplate){
      return
    }
    ctx = ctx || {};
    ctx["title"] = me.appTitle;
    txt = me.navTooltipTemplate.apply(ctx).trim();
    if(txt === ""){
      me.clearNavTabTooltip()
    } else{
      NOC.app.app.setActiveNavTabTooltip(txt)
    }
  },
  //
  clearNavTabTooltip: function(){
    NOC.app.app.clearActiveNavTabTooltip();
  },
});
