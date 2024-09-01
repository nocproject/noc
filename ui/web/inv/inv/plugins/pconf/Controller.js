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
    me.getView().mask(__("Loading..."));
    Ext.Ajax.request({
      url: "/inv/inv/" + me.getView().currentId + "/plugin/pconf/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText),
          view = me.getView();
        view.preview(data);
        view.unmask();
      },
      failure: function(){
        NOC.error(__("Failed to load data"));
        me.getView().unmask();
      },
    });
  },
  onValueChanged: function(data){
    var me = this;
    console.log("Value changed", this.getView().currentId, data);
    Ext.Ajax.request({
      url: "/inv/inv/" + this.getView().currentId + "/plugin/pconf/set/",
      method: 'POST',
      jsonData: data,
      success: function(response){
        var data = Ext.decode(response.responseText);
        if(data.status){
          NOC.info(__("Parameter has been set"));
          me.getView().down("grid").findPlugin("valueedit").cancelEdit();
          me.onReload();
        } else{
          NOC.error(data.message);
        }
      },
      failure: function(){
        NOC.error(__("Failed to set parameter"));
      },
    });
  },
});
