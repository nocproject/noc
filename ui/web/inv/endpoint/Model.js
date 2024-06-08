//---------------------------------------------------------------------
// inv.endpoint Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.endpoint.Model");

Ext.define("NOC.inv.endpoint.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/endpoint/",

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
      name: "resource_domain",
      type: "string",
    },
    {
      name: "resource__label",
      type: "string",
      persist: false,
    },
    {
      name: "discriminator",
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