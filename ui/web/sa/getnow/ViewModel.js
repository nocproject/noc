//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.sa.getnow.ViewModel");
Ext.define("NOC.sa.getnow.ViewModel", {
  extend: "Ext.app.ViewModel",
  alias: "viewmodel.getnow",

  requires: [
    "NOC.sa.getnow.Model",
  ],

  data: {
    total: {
      selection: 0,
    },
    polling: {
      devices: [],
      leave: 0,
      style: "noc-badge-waiting",
      taskId: null,
    },
    isFilterOpen: false,
  },

  formulas: {
    isStarted: function(get){
      return get("polling.style") === "noc-badge-running";
    },
  },

  stores: {
    objectsStore: {
      xclass: "NOC.core.ModelStore",
      model: "NOC.sa.getnow.Model",
      autoLoad: false,
      pageSize: Math.ceil(screen.height / 24),
      leadingBufferZone: Math.ceil(screen.height / 24),
      numFromEdge: Math.ceil(Math.ceil(screen.height / 24) / 2),
      trailingBufferZone: Math.ceil(screen.height / 24),
      purgePageCount: 10,
    },
  },
});