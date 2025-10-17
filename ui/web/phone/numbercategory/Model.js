//---------------------------------------------------------------------
// phone.numbercategory Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.numbercategory.Model");

Ext.define("NOC.phone.numbercategory.Model", {
  extend: "Ext.data.Model",
  rest_url: "/phone/numbercategory/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "is_active",
      type: "boolean",
    },
    {
      name: "rules",
      type: "auto",
    },
    {
      name: "order",
      type: "int",
      defaultValue: 1000,
    },
    {
      name: "name",
      type: "string",
    },
  ],
});
