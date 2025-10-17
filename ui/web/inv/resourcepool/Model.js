//---------------------------------------------------------------------
// inv.resourcepool Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.resourcepool.Model");

Ext.define("NOC.inv.resourcepool.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/resourcepool/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "type",
      type: "string",
    },
    {
      name: "is_unique",
      type: "boolean",
    },
    {
      name: "strategy",
      type: "string",
    },
    {
      name: "api_code",
      type: "string",
    },
    {
      name: "api_role",
      type: "string",
    },
  ],
});