//---------------------------------------------------------------------
// inv.sensorprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.sensorprofile.Model");

Ext.define("NOC.inv.sensorprofile.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/sensorprofile/",

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
      name: "workflow",
      type: "string",
    },
    {
      name: "style",
      type: "int",
    },
    {
      name: "units",
      type: "string",
    },
    {
      name: "metric_type",
      type: "string",
    },
    {
      name: "dynamic_classification_policy",
      type: "string",
      defaultValue: "R",
    },
    {
      name: "enable_collect",
      type: "boolean",
    },
    {
      name: "collect_interval",
      type: "int",
      defaultValue: 60,
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "bi_id",
      type: "int",
      persist: true,
    },
    {
      name: "match_rules",
      type: "auto",
    },
  ],
});