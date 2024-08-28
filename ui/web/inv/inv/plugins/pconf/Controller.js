//---------------------------------------------------------------------
// inv.inv PConf Controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.pconf.Controller");

Ext.define("NOC.inv.inv.plugins.pconf.Controller", {
  extend: "Ext.app.ViewController",
  alias: "controller.pconf",

  onDataChanged: function(store){
    var viewModel = this.getViewModel();
    if(viewModel){
      viewModel.set("totalCount", store.getCount());
    }
  },
  onReload: function(){
    var me = this;
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/pconf/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        this.preview(data);
      },
      failure: function(){
        NOC.error(__("Failed to load data"));
      },
    });
  },
});
