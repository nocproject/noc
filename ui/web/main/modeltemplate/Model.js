//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.main.modeltemplate.Model");
Ext.define("NOC.main.modeltemplate.Model", {
  extend: "Ext.data.Model",
  rest_url: "/main/modeltemplate/",

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
      name: "type",
      type: "string",
    },
    {
      name: "uuid",
      type: "string",
      persist: false,
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "resource_model",
      type: "string",
    },
    {
      name: "params",
      type: "auto",
    },
    {
      name: "params_form",
      type: "auto",
    },
    {
      name: "groups",
      type: "auto",
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "allow_manual",
      type: "boolean",
    },
    {
      name: "default_state",
      type: "string",
    },
    {
      name: "default_state__label",
      type: "string",
      persist: false,
    },
  ],
});
