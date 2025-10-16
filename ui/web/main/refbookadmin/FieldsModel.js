//---------------------------------------------------------------------
// main.refbookadmin FieldsModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.refbookadmin.FieldsModel");

Ext.define("NOC.main.refbookadmin.FieldsModel", {
  extend: "Ext.data.Model",
  rest_url: "/main/refbookadmin/{{parent}}/fields/",
  parentField: "ref_book_id",

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
      name: "order",
      type: "integer",
    },
    {
      name: "is_required",
      type: "boolean",
    },
  ],
});

