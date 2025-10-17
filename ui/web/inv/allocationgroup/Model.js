//---------------------------------------------------------------------
// inv.allocationgroup Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.allocationgroup.Model");

Ext.define("NOC.inv.allocationgroup.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/allocationgroup/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "remote_id",
      type: "string",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "remote_system",
      type: "string",
    },
    {
      name: "remote_system__label",
      type: "string",
      persist: false,
    },
    {
      name: "bi_id",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "labels",
      type: "auto",
    },
  ],
});
