//---------------------------------------------------------------------
// cm.objectvalidationpolicy Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.objectvalidationpolicy.Model");

Ext.define("NOC.cm.objectvalidationpolicy.Model", {
  extend: "Ext.data.Model",
  rest_url: "/cm/objectvalidationpolicy/",

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