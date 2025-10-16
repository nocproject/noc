//---------------------------------------------------------------------
// NOC.core.label.LabelField model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.label.LabelFieldModel");
Ext.define("NOC.core.label.LabelFieldModel", {
  extend: "Ext.data.Model",
  fields: [
    {name: "id", type: "string"},
    {name: "name", type: "string"},
    {name: "scope", type: "string"},
    {name: "value", type: "string"},
    {name: "is_protected", type: "boolean"},
    {name: "bg_color1", type: "string"},
    {name: "bg_color2", type: "string"},
    {name: "fg_color1", type: "string"},
    {name: "fg_color2", type: "string"},
  ],
});
