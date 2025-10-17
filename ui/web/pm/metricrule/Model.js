//---------------------------------------------------------------------
// fm.metricrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricrule.Model");

Ext.define("NOC.pm.metricrule.Model", {
  extend: "Ext.data.Model",
  rest_url: "/pm/metricrule/",

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
      name: "description",
      type: "string",
    },
    {
      name: "is_active",
      type: "boolean",
      defaultValue: true,
    },
    {
      name: "match",
      type: "auto",
    },
    {
      name: "actions",
      type: "auto",
    },
  ],
});
