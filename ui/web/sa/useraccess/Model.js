//---------------------------------------------------------------------
// sa.useraccess Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.useraccess.Model");

Ext.define("NOC.sa.useraccess.Model", {
  extend: "Ext.data.Model",
  rest_url: "/sa/useraccess/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "user",
      type: "int",
    },
    {
      name: "user__label",
      type: "string",
      persist: false,
    },
    {
      name: "administrative_domain",
      type: "int",
    },
    {
      name: "administrative_domain__label",
      type: "string",
      persist: false,
    },
  ],
});
