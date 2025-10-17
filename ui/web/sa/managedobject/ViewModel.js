//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.sa.managedobject.ViewModel");
Ext.define("NOC.sa.managedobject.ViewModel", {
  extend: "Ext.app.ViewModel",
  alias: "viewmodel.managedobject",

  requires: [
    "NOC.sa.managedobject.ApplicationModel",
  ],

  data: {
    total: {
      selection: 0,
      selected: 0,
      all: 0,
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
      model: "NOC.sa.managedobject.ApplicationModel",
      listeners: {
        datachanged: "onSelectedStoreSizeChange",
      },
    },
    selectionStore: {
      xclass: "NOC.core.ModelStore",
      model: "NOC.sa.managedobject.ApplicationModel",
      autoLoad: false,
      pageSize: 70,
      leadingBufferZone: 70,
      numFromEdge: Math.ceil(70 / 2),
      trailingBufferZone: 70,
      purgePageCount: 10,
      listeners: {
        datachanged: "onSelectionStoreSizeChange",
      },
    },
  },
  formulas: {
    hasCreatePerm: function(){
      return this.getView().hasPermission("create");
    },
    hasUpdatePerm: function(){
      return this.getView().hasPermission("update");
    },
    hasRunCmdPerm: function(get){
      return this.getView().hasPermission("commands") && get("total.selected") > 0;
    },
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