//---------------------------------------------------------------------
// sa.credentialcheckrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.credentialcheckrule.Model");

Ext.define("NOC.sa.credentialcheckrule.Model", {
  extend: "Ext.data.Model",
  rest_url: "/sa/credentialcheckrule/",

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
      name: "is_active",
      type: "boolean",
      defaultValue: true,
    },
    {
      name: "preference",
      type: "int",
      defaultValue: 100,
    },
    {
      name: "match",
      type: "auto",
    },
    {
      name: "suggest_snmp",
      type: "auto",
    },
    {
      name: "suggest_credential",
      type: "auto",
    },
    {
      name: "suggest_auth_profile",
      type: "auto",
    },
    {
      name: "suggest_protocols",
      type: "auto",
    },
    {
      name: "suggest_snmp_oids",
      type: "auto",
    },
    {
      name: "match_expression",
      type: "auto",
      persist: false,
    },
  ],
});
