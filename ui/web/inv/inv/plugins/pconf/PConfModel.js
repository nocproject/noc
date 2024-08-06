//---------------------------------------------------------------------
// inv.inv PConfModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.pconf.PConfModel");

Ext.define("NOC.inv.inv.plugins.pconf.PConfModel", {
  extend: "Ext.data.Model",
  fields: [
    {
      name: "name",
      type: "string",
    },
    {
      name: "value",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "units",
      type: "string",
    },
    {
      name: "read_only",
      type: "boolean",
    },
  ],
});
