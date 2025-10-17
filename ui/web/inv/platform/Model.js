//---------------------------------------------------------------------
// inv.platform Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

var convert = function(v){
  if(v instanceof Date){
    return Ext.Date.format(v, "Y-m-d");
  }
  return Ext.Date.parse(v, "Y-m-d");
};

console.debug("Defining NOC.inv.platform.Model");
Ext.define("NOC.inv.platform.Model", {
  extend: "Ext.data.Model",
  rest_url: "/inv/platform/",

  fields: [
    {
      name: "id",
      type: "string",
    },
    {
      name: "vendor",
      type: "string",
    },
    {
      name: "vendor__label",
      type: "string",
      persist: false,
    },
    {
      name: "name",
      type: "string",
    },
    {
      name: "uuid",
      type: "string",
    },
    {
      name: "start_of_sale",
      type: "date",
      convert: convert,
    },
    {
      name: "end_of_sale",
      type: "date",
      convert: convert,
    },
    {
      name: "end_of_support",
      type: "date",
      convert: convert,
    },
    {
      name: "end_of_xsupport",
      type: "date",
      convert: convert,
    },
    {
      name: "snmp_sysobjectid",
      type: "string",
    },
    {
      name: "is_builtin",
      type: "boolean",
      persist: false,
    },
    {
      name: "full_name",
      type: "string",
      persist: false,
    },
    {
      name: "aliases",
      type: "auto",
    },
    {
      name: "labels",
      type: "auto",
    },
  ],
});
