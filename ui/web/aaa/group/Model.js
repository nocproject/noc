//---------------------------------------------------------------------
// aaa.group Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.aaa.group.Model");

Ext.define("NOC.aaa.group.Model", {
  extend: "Ext.data.Model",
  rest_url: "/aaa/group/",

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
      name: "permissions",
      type: "auto",
    },
  ],
});