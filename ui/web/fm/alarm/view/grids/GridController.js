//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.GridController");
Ext.define("NOC.fm.alarm.view.grids.GridController", {
  extend: "Ext.app.ViewController",
  alias: "controller.fm.alarm.GridController",
  //
  onShowMap: function(grid, rowIndex){
    var record = grid.store.getAt(rowIndex);
    NOC.launch("inv.map", "history", {
      args: ["segment", record.get("segment"), record.get("managed_object")],
    });
  },
  //
  onShowObject: function(grid, rowIndex){
    var record = grid.store.getAt(rowIndex);
    NOC.launch("sa.managedobject", "history", {
      args: [record.get("managed_object")],
    });
  },
});
