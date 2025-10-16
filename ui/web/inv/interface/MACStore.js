//---------------------------------------------------------------------
// inv.interface MAC Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.MACStore");

Ext.define("NOC.inv.interface.MACStore", {
  extend: "Ext.data.Store",
  model: null,
  fields: [
    {
      name: "interfaces",
      type: "auto",
    },
    {
      name: "mac",
      type: "string",
    },
    {
      name: "type",
      type: "string",
    },
    {
      name: "vlan_id",
      type: "integer",
    },
  ],
  data: [],
});
