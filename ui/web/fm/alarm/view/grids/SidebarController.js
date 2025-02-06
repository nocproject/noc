//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.SidebarController");

Ext.define("NOC.fm.alarm.view.grids.SidebarController", {
  extend: "Ext.app.ViewController",
  alias: "controller.fm.alarm.sidebar",
  //
  onResetStatuses: function(){
    this.fireViewEvent("fmAlarmSidebarResetSelection");
  },
  onResetFilter: function(){
    this.fireViewEvent("fmAlarmResetFilter");
  },
});
