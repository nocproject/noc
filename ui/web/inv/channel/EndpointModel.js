//---------------------------------------------------------------------
// inv.channel EndpointModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.channel.EndpointModel");

Ext.define("NOC.inv.channel.EndpointModel", {
  extend: "Ext.data.Model",
  rest_url: "/inv/channel/{{parent}}/endpoints/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "channel",
      type: "string",
    },
    {
      name: "channel__label",
      type: "string",
      persist: false,
    },
    {
      name: "resource",
      type: "string",
    },
    {
      name: "is_root",
      type: "boolean",
    },
    {
      name: "pair",
      type: "integer",
    },
    {
      name: "used_by",
      type: "auto",
      persist: false,
    },
  ],
});
