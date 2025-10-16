//---------------------------------------------------------------------
// ip.ipam application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.tools.ToolsModel");

Ext.define("NOC.ip.ipam.view.forms.tools.ToolsModel", {
  extend: "Ext.app.ViewModel",
  alias: "viewmodel.ip.ipam.form.tools",
  requires: [
    "NOC.ip.ipam.model.Prefix",
  ],
  data: {
    ns: null,
    zone: null,
  },
  formulas: {
    isValid: function(get){
      return get("ns") && get("zone");
    },
  },
});
