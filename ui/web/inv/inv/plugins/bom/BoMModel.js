//---------------------------------------------------------------------
// inv.inv BoBModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.bom.BoMModel");

Ext.define("NOC.inv.inv.plugins.bom.BoMModel", {
  extend: "Ext.data.Model",
  fields: [

    {
      name: "id",
      type: "string",
    },
    {
      name: "vendor",
      type: "string",
    },
    {
      name: "model",
      type: "string",
    },
    {
      name: "location",
      type: "auto",
    },
    {
      name: "serial",
      type: "string",
    },
    {
      name: "asset_no",
      type: "string",
    },
    {
      name: "revision",
      type: "string",
    },
    {
      name: "fw_version",
      type: "string",
    },
  ],
});
