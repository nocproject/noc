//---------------------------------------------------------------------
// inv.inv.plugins FileController
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.FileSchemeController");

Ext.define("NOC.inv.inv.plugins.FileSchemeController", {
  extend: "Ext.app.ViewController",
  alias: "controller.filescheme",
  mixins: [
    "NOC.core.mixins.SVGInteraction",
    "NOC.inv.inv.plugins.Mixins",
  ],
  onReload: function(){
    var me = this,
      vm = me.getViewModel(),
      view = me.getView(),
      name = view.itemId.replace("Panel", "").toLowerCase();
    Ext.Ajax.request({
      url: "/inv/inv/" + vm.get("currentId") + "/plugin/" + name + "/",
      method: "GET",
      scope: me,
      success: function(response){
        view.preview(Ext.decode(response.responseText));
        view.down("#zoomControl").reset();
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  //
  onSideChange: function(side){
    var me = this,
      viewModel = me.getViewModel();
    viewModel.set("side", side);
    me.onReload();
  },
  //
  downloadSVG: function(){
    Ext.bind(this.onDownloadSVG, this.getView())();
  },
  //
  onZoom: function(combo, record){
    combo.setZoom(combo, record);
  },
  //
  onSchemeClick: function(event, target){
    console.log("onSchemeClick", event, target);
  },
});
