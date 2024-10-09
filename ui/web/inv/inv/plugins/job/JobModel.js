//---------------------------------------------------------------------
// inv.inv JobModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.job.JobModel");

Ext.define("NOC.inv.inv.plugins.job.JobModel", {
  extend: "Ext.data.Model",
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
      name: "created_at",
      type: "date",
    },
    {
      name: "completed_at",
      type: "date",
    },
    {
      name: "status",
      type: "string",
    },
  ],
});
