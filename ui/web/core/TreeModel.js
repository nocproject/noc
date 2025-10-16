//---------------------------------------------------------------------
// NOC.core.TreeModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.TreeModel");

Ext.define("NOC.core.TreeModel", {
  extend: "Ext.data.Model",

  fields: ["label", "id", "level"],
});