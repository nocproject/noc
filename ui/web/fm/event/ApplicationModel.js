//---------------------------------------------------------------------
// fm.event application view model
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.event.ApplicationModel");

Ext.define("NOC.fm.event.ApplicationModel", {
  extend: "Ext.app.ViewModel",
  alias: "viewmodel.fm.event",
  data: {
    filter: {},
  },
});
