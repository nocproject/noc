//---------------------------------------------------------------------
// NOC.main.soposition.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.soposition.LookupField");

Ext.define("NOC.main.ref.soposition.LookupField", {
  extend: "NOC.core.ComboBox",
  alias: "widget.main.ref.soposition.LookupField",
  uiStyle: "medium-combo",
  pageSize: false,
  askPermission: false,
});
