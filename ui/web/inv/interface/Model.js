//---------------------------------------------------------------------
// inv.interface Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.Model");

Ext.define("NOC.inv.interface.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/interface/",

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
      name: "lag",
      type: "string",
    },
    {
      name: "mac",
      type: "string",
    },
    {
      name: "link",
      type: "string",
    },
    {
      name: "profile",
      type: "string",
    },
    {
      name: "project",
      type: "string",
    },
    {
      name: "state",
      type: "string",
    },
    {
      name: "enabled_protocols",
      type: "auto",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "caps",
      type: "auto",
      persist: false,
    },
    {
      name: "ifindex",
      type: "number",
    },
  ],
});
