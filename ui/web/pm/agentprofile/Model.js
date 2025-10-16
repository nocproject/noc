//---------------------------------------------------------------------
// pm.agentprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.agentprofile.Model");

Ext.define("NOC.pm.agentprofile.Model", {
  extend: "Ext.data.Model",
  rest_url: "/pm/agentprofile/",

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
      name: "zk_check_interval",
      type: "int",
      defaultValue: 60,
    },
    {
      name: "workflow",
      type: "string",
    },
    {
      name: "update_addresses",
      type: "boolean",
      defaultValue: true,
    },
  ],
});