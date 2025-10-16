//---------------------------------------------------------------------
// main.config Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.config.ConfigModel");

Ext.define("NOC.main.config.ConfigModel", {
  extend: "Ext.data.Model",

  fields: [
    {
      name: "section",
      type: "string",
      persist: false,
    },
    {
      name: "key",
      type: "string",
      persist: false,
    },
    {
      name: "default",
      type: "string",
      persist: false,
    },
    {
      name: "value",
      type: "string",
    },
  ],
});
