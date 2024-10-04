//---------------------------------------------------------------------
// sa.job Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.job.Model");

Ext.define("NOC.sa.job.Model", {
  extend: "Ext.data.Model",
  rest_url: "/sa/job/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "parent",
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
      name: "status",
      type: "string",
      defaultValue: "w",
    },
    {
      name: "allow_fail",
      type: "boolean",
    },
    {
      name: "depends_on",
      type: "auto",
    },
    {
      name: "action",
      type: "string",
    },
    {
      name: "inputs",
      type: "auto",
    },
    {
      name: "locks",
      type: "auto",
    },
    {
      name: "environment",
      type: "auto",
    },
    {
      name: "created_at",
      type: "auto",
    },
    {
      name: "started_at",
      type: "auto",
    },
    {
      name: "completed_at",
      type: "auto",
    },
    {
      name: "results",
      type: "auto",
    },
  ],
});