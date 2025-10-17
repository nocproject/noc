//---------------------------------------------------------------------
// kb.entry Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.kb.kbentry2.Model");

Ext.define("NOC.kb.kbentry.Model", {
  extend: "Ext.data.Model",
  rest_url: "/kb/kbentry/",

  fields: [
    {
      name: "id",
      type: "int",
    },
    {
      name: "subject",
      type: "string",
    },
    {
      name: "body",
      type: "string",
    },
    {
      name: "markup_language",
      type: "string",
      defaultValue: "creole",
    },
    {
      name: "language",
      type: "int",
    },
    {
      name: "language__label",
      type: "string",
      persist: false,
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "attachments",
      type: "auto",
    },

  ],
});