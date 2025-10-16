//---------------------------------------------------------------------
// core.Observable simple implement Observable pattern
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Observable");

Ext.define("NOC.core.Observable", {
  requires: [
    "NOC.core.ObservableModel",
    "Ext.data.ArrayStore",
  ],
  qty: 0,

  constructor: function(config){
    this.subscribers = Ext.create("Ext.data.ArrayStore", {
      fields: [
        {name: "key", type: "string"},
        {name: "value"},
      ],
    });
    this.stored = Ext.create("Ext.data.ArrayStore", {
      model: "NOC.core.ObservableModel",
    });
    this.initConfig(config);
    return this;
  },

  next: function(values){
    var me = this;
    this.stored.loadRecords(values);
    this.subscribers.each(function(record){
      var key = record.get("key"),
        cb = record.get("value"),
        valueRecord = me.stored.getById(key);
      if(valueRecord && valueRecord.get("value")){
        cb(valueRecord.get("value"));
      } else{
        console.warn(key + " permission not found");
        cb([]);
      }
    });
  },

  subscribe: function(value){
    this.qty += 1;
    this.subscribers.add(value);
  },

  isLoaded: function(){
    return this.stored.isLoaded();
  },

  getPermissions: function(key){
    var record = this.stored.getById(key);

    if(record){
      return record.get("value");
    }
    return [];
  },
});
