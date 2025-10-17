//---------------------------------------------------------------------
// ip.ipam.prefix form
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.prefix.PrefixController");

Ext.define("NOC.ip.ipam.view.forms.prefix.PrefixController", {
  extend: "Ext.app.ViewController",
  alias: "controller.ip.ipam.prefix.contents",
  // button handlers
  onClose: function(){
    this.fireViewEvent("ipIPAMPrefixListClose");
  },
  onTools: function(){
    var prefix = this.getViewModel().get("prefix");
    this.fireViewEvent("ipIPAMToolsFormOpen", {prefix});
  },
  onAddAddress: function(){
    this.fireViewEvent("ipIPAMAddressFormNew", {address: "create_new"});
  },
  onAddPrefix: function(){
    this.fireViewEvent("ipIPAMPrefixFormNew", {prefix: undefined});
  },
  onDeletePrefix: function(){
    this.fireViewEvent("ipIPAMPrefixDeleteFormOpen");
  },
  onEditPrefix: function(){
    this.fireViewEvent("ipIPAMPrefixFormEdit");
  },
  // bubble event from prefixes dataview
  onAppendPrefix: function(view, params){ // new prefix with name
    this.fireViewEvent("ipIPAMPrefixFormNew", params);
  },
});
