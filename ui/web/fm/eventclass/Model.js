//---------------------------------------------------------------------
// fm.eventclass Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.eventclass.Model");

Ext.define("NOC.fm.eventclass.Model", {
  extend: "Ext.data.Model",
  rest_url: "/fm/eventclass/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "category",
      type: "string",
    },
    {
      name: "description",
      type: "string",
    },
    {
      name: "subject_template",
      type: "string",
    },
    {
      name: "body_template",
      type: "string",
    },
    {
      name: "symptoms",
      type: "string",
    },
    {
      name: "probable_causes",
      type: "string",
    },
    {
      name: "recommended_actions",
      type: "string",
    },
    {
      name: "vars",
      type: "auto",
    },
    {
      name: "text",
      type: "auto",
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "disposition",
      type: "auto",
    },
    {
      name: "link_event",
      type: "boolean",
    },
    {
      name: "action",
      type: "string",
    },
    {
      name: "uuid",
      type: "string",
    },
    {
      name: "is_builtin",
      type: "boolean",
      persist: false,
    },
    {
      name: "handlers",
    },
    {
      name: "deduplication_window",
      type: "integer",
    },
    {
      name: "suppression_window",
      type: "integer",
    },
    {
      name: "ttl",
      type: "integer",
    },
  ],
});
