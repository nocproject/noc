//---------------------------------------------------------------------
// phone.dialplan Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.dialplan.Model");

Ext.define("NOC.phone.dialplan.Model", {
  extend: "Ext.data.Model",
  rest_url: "/phone/dialplan/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "mask",
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
