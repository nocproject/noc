//---------------------------------------------------------------------
// sla.slaprobe Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sla.slaprobe.Model");

Ext.define("NOC.sla.slaprobe.Model", {
  extend: "Ext.data.Model",
  rest_url: "/sla/slaprobe/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "profile",
      type: "string",
    },
    {
      name: "profile__label",
      type: "string",
      persist: false,
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "state",
      type: "string",
    },
    {
      name: "managed_object",
      type: "int",
    },
    {
      name: "managed_object__label",
      type: "string",
      persist: false,
    },
    {
      name: "agent",
      type: "string",
    },
    {
      name: "agent__label",
      type: "string",
      persist: false,
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "group",
      type: "string",
    },
    {
      name: "type",
      type: "string",
    },
    {
      name: "tos",
      type: "int",
    },
    {
      name: "target",
      type: "string",
    },
    {
      name: "hw_timestamp",
      type: "string",
      defaultValue: false,
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "target_id",
      type: "string",
      persist: false,
    },
    {
      name: "bi_id",
      type: "string",
      persist: false,
    },
  ],
});
