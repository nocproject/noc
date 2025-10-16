//---------------------------------------------------------------------
// ip.ipam application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.ApplicationModel");

Ext.define("NOC.ip.ipam.ApplicationModel", {
  extend: "Ext.app.ViewModel",
  alias: "viewmodel.ip.ipam",
  data: {
    activeItem: "ipam-vrf-list",
  },
});