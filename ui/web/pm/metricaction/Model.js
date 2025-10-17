//---------------------------------------------------------------------
// pm.metricaction Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricaction.Model");

Ext.define("NOC.pm.metricaction.Model", {
  extend: "Ext.data.Model",
  rest_url: "/pm/metricaction/",

  fields: [
    {
      name: "id",
      type: "string",
      persist: false,
    },
    {
      name: "name",
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
      name: "params",
      type: "auto",
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
      name: "compose_metric_type",
      type: "string",
    },
    {
      name: "compose_metric_type__label",
      type: "string",
      persist: false,
    },
    {
      name: "activation_config",
      type: "auto",
    },
    {
      name: "deactivation_config",
      type: "auto",
    },
    {
      name: "key_expression",
      type: "string",
    },
    {
      name: "alarm_config",
      type: "auto",
    },
    {
      name: "is_builtin",
      type: "boolean",
      persist: false,
    },
  ],
});
