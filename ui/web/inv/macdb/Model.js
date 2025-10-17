//---------------------------------------------------------------------
// inv.macdb Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.macdb.Model");

Ext.define("NOC.inv.macdb.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/macdb/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "mac",
      type: "string",
    },
    {
      name: "l2_domain",
      type: "string",
    },
    {
      name: "l2_domain__label",
      type: "string",
      persist: false,           
    },
    {
      name: "vlan",
      type: "int",
    },
    {
      name: "managed_object",
      type: "string",
    },
    {
      name: "managed_object__label",
      type: "string",
      persist: false,
    },
    {
      name: "interface",
      type: "string",
    },
    {
      name: "interface__label",
      type: "string",
      persist: false,
    },
    {
      name: "description",
      type: "string",
      persist: false,
    },
    {
      name: "last_changed",
      type: "string",
    },
  ],
});
