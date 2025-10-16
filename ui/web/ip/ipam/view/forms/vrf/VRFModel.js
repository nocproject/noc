//---------------------------------------------------------------------
// ip.ipam application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.vrf.VRFModel");

Ext.define("NOC.ip.ipam.view.forms.vrf.VRFModel", {
  extend: "Ext.app.ViewModel",
  alias: "viewmodel.ip.ipam.form.vrf",
  formulas: {
    isSaveDisabled: function(){
      var app = this.getView().up("[itemId=ip-ipam]");
      return app.hasPermission("launch");
    },
  },
});