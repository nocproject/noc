//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.sa.runcommands.ViewModel");
Ext.define("NOC.sa.runcommands.ViewModel", {
  extend: "Ext.app.ViewModel",
  alias: "viewmodel.runcommands",

  requires: [
    "NOC.sa.runcommands.ApplicationModel",
  ],

  data: {
    total: {
      selection: 0,
      selected: 0,
    },
    progressState: {
      w: 0,
      r: 0,
      s: 0,
      f: 0,
    },
    isRunning: false,
    selectionRow: null,
    selectedRow: null,
  },
  stores: {
    selectedStore: {
      model: "NOC.sa.runcommands.ApplicationModel",
      listeners: {
        datachanged: "onStoreSizeChange",
      },
    },
    selectionStore: {
      xclass: "NOC.core.ModelStore",
      model: "NOC.sa.runcommands.ApplicationModel",
      autoLoad: false,
      pageSize: 70,
      leadingBufferZone: 70,
      numFromEdge: Math.ceil(70 / 2),
      trailingBufferZone: 70,
      purgePageCount: 10,
    },
  },
  formulas: {
    hasRecords: function(get){
      return get("total.selected") > 0;
    },
    selectionGridHasSel: function(get){
      return get("selectionRow") != null;
    },
    selectedGridHasSel: function(get){
      return get("selectedRow") != null;
    },
  },
});