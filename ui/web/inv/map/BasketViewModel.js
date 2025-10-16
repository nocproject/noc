//---------------------------------------------------------------------
// Basket Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.BasketViewModel");

Ext.define("NOC.inv.map.BasketViewModel", {
  extend: "Ext.app.ViewModel",
  alias: "viewmodel.basket",

  data: {
    totalRecords: 0,
  },

  formulas: {
    hasRecords: function(get){
      var store = Ext.StoreManager.lookup("basketStore");
      store.on("datachanged", "calculateRecords", this);
      this.calculateRecords(store);
      return get("totalRecords") > 0;
    },
  },

  calculateRecords: function(store){
    this.set("totalRecords", store.getCount());
  },
});