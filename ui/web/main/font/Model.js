//---------------------------------------------------------------------
// main.font Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.font.Model");

Ext.define("NOC.main.font.Model", {
  extend: "Ext.data.Model",
  rest_url: "/main/font/",

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
      name: "font_family",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "stylesheet_href",
      type: "string",
    },
  ],
});