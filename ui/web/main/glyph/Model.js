//---------------------------------------------------------------------
// main.glyph Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.glyph.Model");

Ext.define("NOC.main.glyph.Model", {
  extend: "Ext.data.Model",
  rest_url: "/main/glyph/",

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
      name: "font",
      type: "string",
    },
    {
      name: "code",
      type: "int",
    },
  ],
});