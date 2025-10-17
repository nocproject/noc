//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.core.filter.CapabilityModel");
Ext.define("NOC.core.filter.CapabilityModel", {
  extend: "Ext.data.TreeModel",

  fields: [
    {
      name: "text",
      type: "string",
    },
    {
      name: "type",
      type: "string",
    },
    {
      name: "typeInclude",
      type: "boolean",
      persist: false,
    },
    {
      name: "typeExclude",
      type: "boolean",
      persist: false,
    },
    {
      name: "id",
      type: "string",
    },
    {
      name: "condition",
      type: "string",
    },
    {
      name: "value",
      type: "string",
    },
    {
      name: "checked",
      defaultValue: false,
      type: "boolean",
    },
  ],
});