//---------------------------------------------------------------------
// wf.wfmigration Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.wfmigration.Model");

Ext.define("NOC.wf.wfmigration.Model", {
  extend: "Ext.data.Model",
  rest_url: "/wf/wfmigration/",

  fields: [
    {
      name: "id",
      type: "string",
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
      name: "migrations",
      type: "auto",
    },
  ],
});
