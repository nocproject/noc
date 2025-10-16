//---------------------------------------------------------------------
// inv.firmwarepolicy Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.firmwarepolicy.Model");

Ext.define("NOC.inv.firmwarepolicy.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/firmwarepolicy/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "status",
      type: "string",
      defaultValue: "a",
    },
    {
      name: "firmware",
      type: "string",
    },
    {
      name: "condition",
      type: "string",
      defaultValue: "=",
    },
    {
      name: "platform",
      type: "string",
    },
    {
      name: "platform__label",
      type: "string",
      persist: false,
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
      name: "description",
      type: "string",
    },
    {
      name: "access_preference",
      type: "string",
    },
    {
      name: "snmp_rate_limit",
      type: "int",
    },
    {
      name: "management",
      type: "auto",
    },
    {
      name: "firmware__label",
      type: "string",
      persist: false,
    },
  ],
});
