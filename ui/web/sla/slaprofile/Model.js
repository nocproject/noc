//---------------------------------------------------------------------
// sla.slaprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sla.slaprofile.Model");

Ext.define("NOC.sla.slaprofile.Model", {
  extend: "Ext.data.Model",
  rest_url: "/sla/slaprofile/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "metrics",
      type: "auto",
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
      name: "metrics_default_interval",
      type: "int",
      defaultValue: 120,
    },
    {
      name: "metrics_interval_buckets",
      type: "int",
      defaultValue: 1,
    },
    {
      name: "test_packets_num",
      type: "int",
      defaultValue: 10,
    },
    {
      name: "raise_alarm_to_target",
      type: "bool",
      defaultValue: false,
    },
    {
      name: "provisioning_policy",
      type: "string",
      defaultValue: "D",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "style",
      type: "string",
    },
    {
      name: "style__label",
      type: "string",
      persist: false,
    },
    {
      name: "bi_id",
      type: "int",
      persist: true,
    },
  ],
});
