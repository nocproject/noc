//---------------------------------------------------------------------
// inv.inv BoM Controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.bom.Controller");

Ext.define("NOC.inv.inv.plugins.bom.Controller", {
  extend: "Ext.app.ViewController",
  alias: "controller.bom",

  onDataChanged: function(store){
    var viewModel = this.getViewModel();
    if(viewModel){
      viewModel.set("totalCount", store.getCount());
    }
  },
  onReload: function(){
    var me = this,
      currentId = me.getViewModel().get("currentId");
    me.getView().mask(__("Loading..."));
    Ext.Ajax.request({
      url: "/inv/inv/" + currentId + "/plugin/bom/",
      method: "GET",
      success: function(response){
        var data = Ext.decode(response.responseText),
          view = me.getView();
        view.preview(data, currentId);
        view.unmask();
      },
      failure: function(){
        NOC.error(__("Failed to load data"));
        me.getView().unmask();
      },
    });
  },
  onBeforeStoreLoad: function(store){
    console.log("onBeforeStoreLoad ", store);
  },
});