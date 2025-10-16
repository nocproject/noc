//---------------------------------------------------------------------
// main.refbookadmin Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.refbookadmin.Model");

Ext.define("NOC.main.refbookadmin.Model", {
  extend: "Ext.data.Model",
  rest_url: "/main/refbookadmin/",

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
      name: "download_url",
      type: "string",
    },
    {
      name: "downloader",
      type: "string",
    },
    {
      name: "is_builtin",
      type: "boolean",
      defaultValue: false,
    },
    {
      name: "is_enabled",
      type: "boolean",
      defaultValue: false,
    },
    {
      name: "language",
      type: "string",
    },
    {
      name: "refresh_interval",
      type: "string",
    },
    {
      name: "last_updated",
      type: "date",
    },
    {
      name: "next_update",
      type: "date",
    },
  ],
});