//---------------------------------------------------------------------
// NOC.core.ModelStore
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.InlineModelStore");

Ext.define("NOC.core.InlineModelStore", {
  extend: "Ext.data.Store",
  filterParams: undefined,
  url: undefined,
  model: undefined,
  remoteSort: true,
  remoteFilter: true,
  autoLoad: false,
  alias: "store.inlinestore",

  constructor: function(config){
    var me = this,
      model = Ext.create(config.model),
      fields = model.fields.items,
      defaultValues = {};

    me.rootProperty = model.rootProperty ? model.rootProperty : "data";
    me.parentField = model.parentField;
    me.restUrl = model.rest_url;
    me.isLocal = model.isLocal;
    for(var i = 0; i < fields.length; i++){
      var field = fields[i],
        dv = field.defaultValue;
      if(dv !== undefined){
        defaultValues[field.name] = dv;
      }
    }
    me._proxy = Ext.create("Ext.data.RestProxy", {
      url: me.restUrl,
      pageParam: "__page",
      startParam: "__start",
      limitParam: "__limit",
      sortParam: "__sort",
      extraParams: {
        "__format": "ext",
      },
      reader: {
        type: "json",
        rootProperty: me.rootProperty,
        totalProperty: "total",
        successProperty: "success",
      },
      writer: {
        type: "json",
      },
      listeners: {
        exception: {
          scope: me,
          fn: me.onSyncException,
        },
      },
    });
    Ext.apply(config, {
      // model: config.model,
      model: null,
      fields: fields, // Removed by superclass constructor
      defaultValues: defaultValues,
      implicitModel: "Ext.data.Model",
      proxy: me._proxy,
      listeners: {
        write: {
          scope: me,
          fn: me.onSyncWrite,
        },
      },
      syncConfig: {},
    });
    //me.syncConfig = {};
    me.callParent([config]);
  },

  setFilterParams: function(config){
    var me = this;
    me.filterParams = Ext.Object.merge({}, config);
    // Forcefully go to first page
    me.currentPage = 1;
  },

  load: function(config){
    var me = this;
    config = Ext.Object.merge({
      params: Ext.Object.merge({}, me.filterParams),
    }, config);
    // Override callback
    // @todo: Call original callback
    config = Ext.Object.merge(config, {
      callback: function(records, operation, success){
        if(!success)
          NOC.error(__("Failed to fetch data!"));
      },
    });
    // Continue loading
    me.callParent([config]);
  },
  // override sync()
  sync: function(config){
    var me = this,
      conf = config || {};
    me.syncConfig = Ext.Object.merge({}, conf);
    if(!me.getNewRecords().length && !me.getUpdatedRecords().length
            && !me.getRemovedRecords().length){
      // No changed records, call success callback
      Ext.callback(me.syncConfig.success,
                   me.syncConfig.scope || me);
    } else{
      // Having changed records. Start sync process
      me.callParent();
    }
  },
  onSyncWrite: function(){
    var me = this;
    Ext.callback(me.syncConfig.success,
                 me.syncConfig.scope || me);
  },
  onSyncException: function(proxy, request, op){
    var me = this;
    Ext.callback(me.syncConfig.failure,
                 me.syncConfig.scope || me, [request, op, 500]);
  },
  setParent: function(parentId){
    var me = this;
    me._proxy.url = me.restUrl.replace("{{parent}}", parentId);
  },
  // clone all content
  cloneData: function(){
    // @todo: Clone existing data
  },
});
