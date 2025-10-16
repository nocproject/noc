//---------------------------------------------------------------------
// pm.metrictype Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metrictype.Model");

Ext.define("NOC.pm.metrictype.Model", {
  extend: "Ext.data.Model",
  rest_url: "/pm/metrictype/",

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
      name: "scope",
      type: "string",
    },
    {
      name: "scope__label",
      type: "string",
      persist: false,
    },
    {
      name: "field_name",
      type: "string",
    },
    {
      name: "field_type",
      type: "string",
    },
    {
      name: "units",
      type: "string",
    },
    {
      name: "units__label",
      type: "string",
      persist: false,
    },
    {
      name: "scale",
      type: "string",
    },
    {
      name: "is_delta",
      type: "boolean",
    },
    {
      name: "scale__label",
      type: "string",
      persist: false,
    },
    {
      name: "compose_inputs",
      type: "auto",
    },
    {
      name: "compose_expression",
      type: "string",
    },
    {
      name: "collector_mappings",
      type: "auto",
    },
    {
      name: "is_builtin",
      type: "boolean",
      persist: false,
    },
  ],
});
