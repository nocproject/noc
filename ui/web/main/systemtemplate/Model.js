//---------------------------------------------------------------------
// main.systemtemplate Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.systemtemplate.Model");

Ext.define("NOC.main.systemtemplate.Model", {
  extend: "Ext.data.Model",
  rest_url: "/main/systemtemplate/",

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
      name: "template__label",
      type: "string",
      persist: false,
    },
    {
      name: "template",
      type: "string",
    },
  ],
});
