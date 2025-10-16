//---------------------------------------------------------------------
// ip.ipam application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.prefix.PrefixModel");

Ext.define("NOC.ip.ipam.view.forms.prefix.PrefixModel", {
  extend: "Ext.app.ViewModel",
  alias: "viewmodel.ip.ipam.prefix.contents",
  requires: [
    "NOC.ip.ipam.model.Prefix",
    "NOC.ip.ipam.model.Address",
    "NOC.ip.ipam.model.Range",
  ],
  formulas: {
    noFreePrefixes: function(get){
      return get("prefix.prefixes").filter(function(el){
        return el.isFree;
      }).length === 0;
    },
    noFreeAddresses: function(get){
      return get("prefix.addresses").filter(function(el){
        return el.isFree;
      }).length === 0;
    },
    noPrefixes: function(get){
      return get("prefix.prefixes").length === 0;
    },
    noAddresses: function(get){
      return get("prefix.addresses").length === 0;
    },
    noRanges: function(get){
      return get("prefix.ranges").length === 0;
    },
    // isSaveDisabled: function() {
    //     var app = this.getView().up("[itemId=ip-ipam]");
    //     return app.hasPermission("launch");
    // }
  },
  stores: {
    bookmarkStore: {
      data: "{prefix.bookmarks}",
    },
    prefixStore: {
      model: "NOC.ip.ipam.model.Prefix",
      data: "{prefix.prefixes}",
      filters: [
        function(record){
          return !record.get("isFree");
        },
      ],
    },
    addressStore: {
      model: "NOC.ip.ipam.model.Address",
      data: "{prefix.addresses}",
      filters: [
        function(record){
          return !record.get("isFree");
        },
      ],
    },
    rangeStore: {
      model: "NOC.ip.ipam.model.Range",
      data: "{prefix.ranges}",
    },
  },
});