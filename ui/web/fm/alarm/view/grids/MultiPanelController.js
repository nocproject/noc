//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.MultiPanelController");
Ext.define("NOC.fm.alarm.view.grids.MultiPanelController", {
  extend: "Ext.app.ViewController",
  alias: "controller.fm.alarm.multipanel",
  onDataChanged: function(store){
    var mapping = function(record){
        return {
          id: record.id,
          label: record.get("label"),
          type: record.get("type"),
          icon: record.get("icon"),
        };
      },
      getIcons = function(record){
        if(record.icon){
          return "<i class='" + record.icon + "' aria-hidden='true' title='" + record.label + "'></i>&nbsp;";
        } else{
          return "<span>" + record.label + "</span>&nbsp;";
        }
      },
      records = store.data.items,
      newValue = records.map(mapping);
    this.getViewModel().set("array", newValue);
    this.getView().setValue({
      array: newValue,
      include: this.getViewModel().get("include"),
    }, true);
    this.getView().setHtml(newValue.map(getIcons).join(""));
  },
});