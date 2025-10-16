//---------------------------------------------------------------------
// inv.vendor Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.vendor.Model");

Ext.define("NOC.inv.vendor.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/vendor/",

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
      name: "full_name",
      type: "string",
    },
    {
      name: "code",
      type: "auto",
    },
    {
      name: "uuid",
      type: "string",
      persist: false,
    },
    {
      name: "site",
      type: "string",
    },
    {
      name: "is_builtin",
      type: "boolean",
      persist: false,
    },
  ],
});
