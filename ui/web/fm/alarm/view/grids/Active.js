//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.Active");

Ext.define("NOC.fm.alarm.view.grids.Active", {
  extend: "NOC.fm.alarm.view.grids.Grid",
  alias: "widget.fm.grid.active",
  stateful: true,
  stateId: "fm.grid.activeGrid",
  viewModel: {
    type: "fm.alarm.sidebar",
  },
  requires: [
    "NOC.fm.alarm.view.grids.SidebarModel",
    "NOC.fm.alarm.view.grids.Grid",
  ],
  selModel: {
    mode: "MULTI",
    selType: "checkboxmodel",
  },
  listeners: {
    selectionchange: function(sel){
      this.getController().fireViewEvent("fmAlarmSelectionChange", sel);
    },
  },
  bind: {
    selection: "{total.activeAlarmsSelected}",
  },
  emptyText: __("No active alarms"),
  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      store: {
        type: "fm.alarm",
        listeners: {
          scope: me,
          load: this.onAlarmsLoad,
        },
      },
    });
    this.callParent();
  },
  // total fill
  onAlarmsLoad: function(store){
    this.getController().fireViewEvent("fmAlarmLoaded", store);
  },
  // calc
  onAlarmsSelected: function(sel){
    this.getController().fireViewEvent("fmAlarmSelectionChange", sel);
  },
});
