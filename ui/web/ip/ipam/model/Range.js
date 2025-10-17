//---------------------------------------------------------------------
// ip.ipam Range Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.model.Range");

Ext.define("NOC.ip.ipam.model.Range", {
  extend: "Ext.data.Model",
  fields: [
    {
      name: "name",
      type: "string",
    },
    {
      name: "from_address",
      type: "string",
    },
    {
      name: "to_address",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
  ],
});