//---------------------------------------------------------------------
// cm.interfacevalidationpolicy Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.interfacevalidationpolicy.Model");

Ext.define("NOC.cm.interfacevalidationpolicy.Model", {
  extend: "Ext.data.Model",
  rest_url: "/cm/interfacevalidationpolicy/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "rules",
      type: "auto",
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
      name: "filter_query",
      type: "string",
    },
    {
      name: "filter_query__label",
      type: "string",
      persist: false,
    },
  ],
});