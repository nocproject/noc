//---------------------------------------------------------------------
// inv.techdomain Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.techdomain.Model");

Ext.define("NOC.inv.techdomain.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/techdomain/",

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
      name: "uuid",
      type: "string",
      persist: false,
    },
    {
      name: "code",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "kind",
      type: "string",
    },
    {
      name: "channel_discriminator",
      type: "string",
    },
    {
      name: "endpoint_discriminator",
      type: "string",
    },
    {
      name: "max_endpoints",
      type: "int",
    },
    {
      name: "allow_parent",
      type: "boolean",
    },
    {
      name: "allow_children",
      type: "boolean",
    },
    {
      name: "allow_p2p",
      type: "boolean",
    },
    {
      name: "allow_up2p",
      type: "boolean",
    },
    {
      name: "allow_bunch",
      type: "boolean",
    },    
    {
      name: "allow_p2mp",
      type: "boolean",
    },
    {
      name: "allow_up2mp",
      type: "boolean",
    },
    {
      name: "allow_star",
      type: "boolean",
    },
    {
      name: "controller_handler",
      type: "string",
    },
    {
      name: "bi_id",
      type: "int",
      persist: false,
    },
  ],
});
