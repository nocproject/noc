//---------------------------------------------------------------------
// main.metricstream Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.metricstream.Model");

Ext.define("NOC.main.metricstream.Model", {
  extend: "Ext.data.Model",
  rest_url: "/main/metricstream/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "scope",
      type: "string",
    },
    {
      name: "scope__label",
      type: "string",
      persist: false,
    },
    {
      name: "is_active",
      type: "boolean",
      defaultValue: true,
    },
    {
      name: "fields",
      type: "auto",
    },
  ],
});
