//---------------------------------------------------------------------
// inv.inv BoM Controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.bom.BoMController");

Ext.define("NOC.inv.inv.plugins.bom.BoMController", {
  extend: "Ext.app.ViewController",
  alias: "controller.bom",
  mixins: [
    "NOC.core.mixins.Export",
  ],
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
  //
  onExport: function(){
    var grid = this.getView().down("grid"),
      store = grid.getStore(),
      columns,
      date = "_" + Ext.Date.format(new Date(), "YmdHis"),
      filename = "bom_" + date + ".csv",
      maxLocationLength = 0, exportRecords = [];

    store.each(function(record){
      var location = record.get("location"),
        data = record.getData(),
        dataCopy = Ext.apply({}, data); 
      
      if(Array.isArray(location) && location.length > maxLocationLength){
        maxLocationLength = location.length;
      }
      for(var i = 0; i < location.length; i++){
        dataCopy['location' + (i + 1)] = location[i];
      }
      exportRecords.push(Ext.create("Ext.data.Model", dataCopy));
    });

    columns = grid.getColumns().map(function(column){
      return {
        dataIndex: column.dataIndex,
      };
    });
    for(var i = 0; i < maxLocationLength; i++){
      columns.push({
        dataIndex: 'location' + (i + 1),
      });
    }

    columns = Ext.Array.filter(columns, function(column){
      return column.dataIndex !== "location";
    });
    
    this.downloadCsv(
      new Blob([this.export(exportRecords, columns)],
               {type: "text/plain;charset=utf-8"}),
      filename,
    );
  },
});
