//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.controller.Grid");

Ext.define("NOC.sa.discoveredobject.controller.Grid", {
  extend: "Ext.app.ViewController",
  alias: "controller.sa.discoveredobject.grid",

  checksRenderer: function(v){
    var result = [];
    Ext.Array.each(v, function(item){
      var text = item.label + (item.port ? ":" + item.port : ""),
        background = "background:" + (item.status ? "lightgreen;" : "goldenrod;"),
        border = "border:" + (item.status ? "green" : "red") + " 1px solid;";

      result.push("<span style='" + border + background + "padding:1;margin:2;'>" + text + "</span>");
    });
    return result.join("") || __("N/A");
  },
  afterrenderHandler: function(grid){
    grid.up().lookup("sa-discovered-sidebar").getController().reload();
    grid.getStore().on("load", function(store){
      var viewModel = grid.up().getViewModel();
      if(viewModel){
        viewModel.set("total.all", store.getTotalCount());
      }
    });

  },
  onSelectAll: function(combo, record){
    var renderPlugin, grid = this.getView();

    switch(record.get("cmd")){
      case"SCREEN": {
        renderPlugin = grid.findPlugin("bufferedrenderer");
        grid.getSelectionModel().selectRange(0, renderPlugin.getLastVisibleRowIndex());
        return;
      }
      case"N_ROWS": {
        Ext.Msg.prompt(__("Select rows"), __("Please enter number:"), function(btn, text){
          if(btn === "ok"){
            this.getNRows(grid, "0", text);
          }
        }, this);
        break;
      }
      case"PERIOD": {
        Ext.Msg.prompt(__("Select period"), __("Please enter period (start,qty), first pos is 0:"), function(btn, text){
          if(btn === "ok"){
            this.getNRows(grid, text.split(",")[0], text.split(",")[1]);
          }
        }, this);
        break;
      }
      default: {
        this.getNRows(grid, "0", record.get("cmd").slice(6));
      }
    }
    combo.setValue(null);
  },
  onUnselectAll: function(){
    this.getView().getSelectionModel().deselectAll();
  },
  onGridStoreSizeChange: function(selModel){
    this.getViewModel().set("total.selected", selModel.getCount());
  },
  onGridRefresh: function(){
    this.getView().mask(__("Loading"));
    this.getView().getStore().reload({
      callback: function(){
        this.getView().unmask();
      },
      scope: this,
    });
  },
  getNRows: function(selectionGrid, m, n){
    var limit = Number.parseInt(n),
      start = Number.parseInt(m);
    if(Number.isInteger(limit) && Number.isInteger(start)){
      selectionGrid.mask(__("Loading"));
      selectionGrid.getStore().reload({
        callback: function(){
          selectionGrid.unmask();
          selectionGrid.getSelectionModel().selectRange(start, start + limit - 1);
        },
      });
    }
  },
});
