//---------------------------------------------------------------------
// bi.dashboardlayout Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.bi.dashboardlayout.Model");

Ext.define("NOC.bi.dashboardlayout.Model", {
  extend: "Ext.data.Model",
  rest_url: "/bi/dashboardlayout/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "cells",
      type: "auto",
    },
    {
      name: "description",
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
  ],
});
