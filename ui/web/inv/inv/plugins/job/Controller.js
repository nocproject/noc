//---------------------------------------------------------------------
// inv.inv Job Controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.job.Controller");

Ext.define("NOC.inv.inv.plugins.job.Controller", {
  extend: "Ext.app.ViewController",
  alias: "controller.job",
  //
  onDataChanged: function(store){
    var viewModel = this.getViewModel();
    if(viewModel){
      viewModel.set("totalCount", store.getCount());
    }
  },
  //
  onReload: function(){
    var me = this,
      currentId = me.getViewModel().get("currentId");
    me.getView().mask(__("Loading..."));
    Ext.Ajax.request({
      url: "/inv/inv/" + currentId + "/plugin/job/",
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
  //
  onViewJob: function(view, rowIndex){
    var r = view.getStore().getAt(rowIndex),
      id = r.get("id");
    this.viewJob(view, id);
  },
  //
  onRowDblClick: function(view, record){
    this.viewJob(view, record.id);
  },
  //
  viewJob: function(view, objectId){
    var grid = view.up("gridpanel");
    grid.mask(__("Loading..."));
    NOC.launch("sa.job", "history", {"args": [objectId]});
    setTimeout(function(){
      grid.unmask();
    }, 500);    
  },
});
