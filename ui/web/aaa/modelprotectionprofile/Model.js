//---------------------------------------------------------------------
// aaa.modelprotectionprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.aaa.modelprotectionprofile.Model");

Ext.define("NOC.aaa.modelprotectionprofile.Model", {
  extend: "Ext.data.Model",
  rest_url: "/aaa/modelprotectionprofile/",

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
      name: "model",
      type: "string",
    },
    {
      name: "field_access",
      type: "auto",
    },
    {
      name: "groups",
      type: "auto",
    },
  ],
});
