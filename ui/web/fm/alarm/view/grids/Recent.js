//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.main.Recent");

Ext.define("NOC.fm.alarm.view.grids.Recent", {
  extend: "NOC.fm.alarm.view.grids.Grid",
  alias: "widget.fm.alarm.recent",
  stateful: true,
  stateId: "fm.grid.recentGrid",
  requires: [
    "NOC.fm.alarm.store.Alarm",
    "NOC.fm.alarm.view.grids.SidebarModel",
    "NOC.fm.alarm.view.grids.Grid",
  ],
  emptyText: __("No recently closed alarms"),
  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      store: {
        type: "fm.alarm",
      },
    });
    this.callParent();
  },
});