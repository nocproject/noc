//---------------------------------------------------------------------
// NOC.main.refbookadmin.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.refbookadmin.LookupField");

Ext.define("NOC.main.refbookadmin.LookupField", {
  extend: "Ext.form.field.ComboBox",
  alias: "widget.main.refbookadmin.LookupField",
  queryMode: "local",
  valueField: "value",
  editable: false,
  store: {
    fields: ["value", "text"],
    data: [
      {"value": "string", "text": __("string")},
      {"value": "substring", "text": __("substring")},
      {"value": "starting", "text": __("starting")},
      {"value": "mac_3_octets_upper", "text": __("3 Octets of the MAC")},
    ],
  },
});
