//---------------------------------------------------------------------
// pm.agent Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.agent.Model");

Ext.define("NOC.pm.agent.Model", {
  extend: "Ext.data.Model",
  rest_url: "/pm/agent/",

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
      name: "profile",
      type: "string",
    },
    {
      name: "zk_check_interval",
      type: "int",
    },
    {
      name: "serial",
      type: "string",
    },
    {
      name: "ip",
      type: "auto",
    },
    {
      name: "mac",
      type: "auto",
    },
    {
      name: "state",
      type: "string",
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "effective_labels",
      type: "auto",
      persist: false,
    },
    {
      name: "key",
      type: "string",
      persist: true,
    },
    {
      name: "bi_id",
      type: "string",
      persist: false,
    },
  ],
});