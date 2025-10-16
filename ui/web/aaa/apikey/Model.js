//---------------------------------------------------------------------
// aaa.apikey Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.aaa.apikey.Model");

Ext.define("NOC.aaa.apikey.Model", {
  extend: "Ext.data.Model",
  rest_url: "/aaa/apikey/",

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
      name: "expires",
      type: "auto",
    },
    {
      name: "is_active",
      type: "boolean",
    },
    {
      name: "access",
      type: "auto",
    },
    {
      name: "acl",
      type: "auto",
    },
    {
      name: "key",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
  ],
});
