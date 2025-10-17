//---------------------------------------------------------------------
// ip.ipam application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.GridController");
Ext.define("NOC.ip.ipam.view.GridController", {
  extend: "Ext.app.ViewController",
  alias: "controller.ip.ipam.GridController",
  onFavItem: function(grid, rowIndex){
    var store = this.getView().getStore(),
      record = store.getAt(rowIndex),
      id = record.get(store.getModel().idProperty),
      action = record.get("fav_status") ? "reset" : "set",
      url = store.getProxy().url + "favorites/item/" + id + "/" + action + "/";

    Ext.Ajax.request({
      url: url,
      method: "POST",
      success: function(){
        // Invert current status
        record.set("fav_status", !record.get("fav_status"));
        grid.refresh();
      },
    });
  },
  onEditItem: function(grid, rowIndex){
    var store = this.getView().getStore(),
      record = store.getAt(rowIndex);
    this.fireViewEvent("ipIPAMVRFFormEdit", record);
  },
  onOpenCard: function(grid, rowIndex, colIndex, item, e, record){
    window.open(
      "/api/card/view/prefix/" + record.get("id") + "/",
    );
  },
  onViewRootPrefix4: function(view, rowIndex, colIndex, item, e, record){
    if(record.get("afi_ipv4")){
      this.onOpenContents(record.id, 4);
    }
  },
  onViewRootPrefix6: function(view, rowIndex, colIndex, item, e, record){
    if(record.get("afi_ipv6")){
      this.onOpenContents(record.id, 6);
    }
  },
  onOpenContents: function(id, afi){
    this.fireViewEvent("ipIPAMViewPrefixContents", {id: id, afi: afi});
  },
});