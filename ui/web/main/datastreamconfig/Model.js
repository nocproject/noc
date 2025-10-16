//---------------------------------------------------------------------
// main.datastreamconfig Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.datastreamconfig.Model");

Ext.define("NOC.main.datastreamconfig.Model", {
  extend: "Ext.data.Model",
  rest_url: "/main/datastreamconfig/",

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
      name: "formats",
      type: "auto",
    },
  ],
});