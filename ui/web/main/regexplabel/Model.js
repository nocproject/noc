//---------------------------------------------------------------------
// main.regexplabel Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.regexplabel.Model");

Ext.define("NOC.main.regexplabel.Model", {
  extend: "Ext.data.Model",
  rest_url: "/main/regexplabel/",

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
      name: "regexp",
      type: "string",
    },
    {
      name: "regexp_compiled",
      type: "string",
      persist: false,
    },
    {
      name: "flag_multiline",
      type: "boolean",
    },
    {
      name: "flag_dotall",
      type: "boolean",
    },
    {
      name: "labels",
      type: "auto",
    },
    {
      name: "enable_managedobject_name",
      type: "boolean",
    },
    {
      name: "enable_managedobject_address",
      type: "boolean",
    },
    {
      name: "enable_managedobject_description",
      type: "boolean",
    },
    {
      name: "enable_interface_name",
      type: "boolean",
    },
    {
      name: "enable_interface_description",
      type: "boolean",
    },
    {
      name: "enable_sensor_local_id",
      type: "boolean",
    },   
  ],
});