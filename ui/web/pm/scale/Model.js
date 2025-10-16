//---------------------------------------------------------------------
// pm.scale Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.scale.Model");

Ext.define("NOC.pm.scale.Model", {
  extend: "Ext.data.Model",
  rest_url: "/pm/scale/",

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
      name: "uuid",
      type: "string",
    },
    {
      name: "code",
      type: "string",
    },
    {
      name: "label",
      type: "string",
    },
    {
      name: "base",
      type: "int",
      defaultValue: 10,
    },
    {
      name: "exp",
      type: "int",
    },
  ],
});