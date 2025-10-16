//---------------------------------------------------------------------
// ip.ipam Address Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.model.Address");

Ext.define("NOC.ip.ipam.model.Address", {
  extend: "Ext.data.Model",
  fields: [
    {
      name: "prefix",
      type: "int",
    },
    {
      name: "vrf",
      type: "int",
    },
    {
      name: "address",
      type: "string",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "fqdn",
      type: "string",
    },
    {
      name: "mac",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "afi",
      type: "int",
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "tt",
      type: "string",
    },
    {
      name: "state",
      type: "string",
    },
    {
      name: "project",
      type: "string",
    },
    {
      name: "managed_object",
      type: "string",
    },
    {
      name: "subinterface",
      type: "string",
    },
    {
      name: "source",
      type: "string",
    },
    {
      name: "allocated_till",
      type: "string",
    },
    // {
    //     name: "direct_permissions",
    //     type: "auto"
    // },
    {
      name: "isFree",
      type: "boolean",
      persist: false,
    },
  ],
});
