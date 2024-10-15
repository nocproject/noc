//---------------------------------------------------------------------
// inv.inv.plugins.rack Controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.rack.RackController");

Ext.define("NOC.inv.inv.plugins.rack.RackController", {
  extend: "NOC.inv.inv.plugins.FileSchemeController",
  alias: "controller.rack",
  //
  onDataChanged: function(store){
    var viewModel = this.getViewModel();
    if(viewModel){
      viewModel.set("totalCount", store.getCount());
    }
  },
  //
  onCellValidateEdit: function(){
    return true;
  },
  //
  onCellEdit: function(editor, context){
    var me = this,
      viewModel = me.getViewModel();
    if(context.field === "position_front"){
      context.record.set("position_rear", 0);
    }
    if(context.field === "position_rear"){
      context.record.set("position_front", 0);
    }
    // Submit
    Ext.Ajax.request({
      url: "/inv/inv/" + viewModel.get("currentId") + "/plugin/rack/rackload/",
      method: "POST",
      scope: me,
      jsonData: {
        cid: context.record.get("id"),
        position_front: context.record.get("position_front"),
        position_rear: context.record.get("position_rear"),
        shift: context.record.get("shift"),
      },
      loadMask: me,
      success: function(){
        me.onReload();
      },
      failure: function(){
        NOC.error(__("Failed to save"));
      },
    });
  },
});
