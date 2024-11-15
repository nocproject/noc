//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.DisplayFilter");

Ext.define("NOC.fm.alarm.view.grids.DisplayFilter", {
  extend: "Ext.container.Container",
  alias: "widget.fm.alarm.display",
  controller: "fm.alarm.display",
  requires: [
    "NOC.fm.alarm.view.grids.DisplayFilterController",
    "NOC.fm.alarm.view.grids.MultiPanel",
    "NOC.fm.alarm.view.grids.DurationFilter",
  ],
  border: false,
  defaults: {
    margin: "5 0",
  },
  items: [
    {
      xtype: "fm.alarm.multipanel",
      title: __("Service Profiles"),
      searchStore: "fm.profile",
      bind: {value: "{displayFilter.hasProfiles}"},
    },
    {
      xtype: "fm.alarm.filter.duration",
      fieldLabel: __("Recent Alarms (time/opacity)"),
      labelAlign: "top",
      bind: {value: "{displayFilter.duration}"},
    },
  ],
});