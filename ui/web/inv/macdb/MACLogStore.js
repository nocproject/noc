//---------------------------------------------------------------------
// MAC Log Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.macdb.MACLogStore");

Ext.define("NOC.inv.macdb.MACLogStore", {
  extend: "Ext.data.Store",
  fields: [
    {
      name: "mac",
      type: "string",
    },
    {
      name: "vlan",
      type: "integer",
    },
    {
      name: "managed_object_name",
      type: "string",
    },
    {
      name: "interface_name",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "timestamp",
      type: "string",
    },

  ],
  data: [],
});
