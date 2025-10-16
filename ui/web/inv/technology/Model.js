//---------------------------------------------------------------------
// inv.technology Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.technology.Model");

Ext.define("NOC.inv.technology.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/technology/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "uuid",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "service_model",
      type: "string",
    },
    {
      name: "client_model",
      type: "string",
    },
    {
      name: "single_service",
      type: "boolean",
    },
    {
      name: "single_client",
      type: "boolean",
    },
    {
      name: "allow_children",
      type: "boolean",
    },
    {
      name: "service_model__label",
      type: "string",
      persist: false,
    },
    {
      name: "client_model__label",
      type: "string",
      persist: false,
    },
  ],
});
