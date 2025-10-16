//---------------------------------------------------------------------
// ip.addressrange Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.addressrange.Model");

Ext.define("NOC.ip.addressrange.Model", {
  extend: "Ext.data.Model",
  rest_url: "/ip/addressrange/",

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
      name: "is_active",
      type: "boolean",
      defaultValue: false,
    },
    {
      name: "vrf",
      type: "string",
    },
    {
      name: "vrf__label",
      type: "string",
      persist: false,
    },
    {
      name: "afi",
      type: "string",
    },
    {
      name: "from_address",
      type: "string",
    },
    {
      name: "to_address",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "is_locked",
      type: "boolean",
      defaultValue: false,
    },
    {
      name: "action", 
      type: "string",
      defaultValue: "N",
    },
    {
      name: "fqdn_template", 
      type: "string",
    },
    {
      name: "reverse_nses",
      type: "string",
    },
    {
      name: "labels",
      type: "string",
    },
    {
      name: "tt",
      type: "int",
    },
    {
      name: "allocated_till",         
      type: "date",
    },
  ],
});

