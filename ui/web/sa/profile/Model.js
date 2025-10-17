//---------------------------------------------------------------------
// sa.profile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.profile.Model");

Ext.define("NOC.sa.profile.Model", {
  extend: "Ext.data.Model",
  rest_url: "/sa/profile/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "uuid",
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
  ],
});
