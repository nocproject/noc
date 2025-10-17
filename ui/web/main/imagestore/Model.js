//---------------------------------------------------------------------
// main.imagestore Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.imagestore.Model");

Ext.define("NOC.main.imagestore.Model", {
  extend: "Ext.data.Model",
  rest_url: "/main/imagestore/",

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
      name: "type",
      type: "string",
    },
    {
      name: "content_type",
      type: "string",
      persist: false,
    },
    {
      name: "filename",
      type: "string",
      persist: false,
    },
    {
      name: "file",
      type: "auto",
    },
  ],
});
