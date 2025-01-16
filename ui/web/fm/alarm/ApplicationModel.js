//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.ApplicationModel");

Ext.define("NOC.fm.alarm.ApplicationModel", {
  extend: "Ext.app.ViewModel",
  alias: "viewmodel.fm.alarm",
  data: {
    activeFilter: {},
    recentFilter: {},
    displayFilter: {},
    selected: {},
    activeItem: "fm-alarm-list",
    containerDisabled: false,
  },
});