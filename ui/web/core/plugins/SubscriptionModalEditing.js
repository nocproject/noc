//---------------------------------------------------------------------
// NOC.core.plugins SubscriptionModalEditing for grid cell editing
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.plugins.SubscriptionModalEditing");

Ext.define("NOC.core.plugins.SubscriptionModalEditing", {
  extend: "Ext.AbstractPlugin",
  alias: "plugin.subscriptionmodalediting",
  requires: [
    "Ext.window.Window",
    "Ext.form.Panel",
  ],
  dataIndex: "allow_subscribe", // Field name to edit
  //
  init: function(grid){
    this.grid = grid;
    grid.on("beforecellclick", function(view, cell, cellIndex, record, tr, rowIndex, e){
      var column = e.position.column;
      if(column && column.dataIndex == this.dataIndex){
        this.urlPrefix = column.urlPrefix || "urlPrefix_not_set";
        this.showEditor(record, column, view, cell);
        return false; // Prevent default cell click action
      }
      return true;
    }, this);
  },

  showEditor: function(record){
    this.formPanel = Ext.create("Ext.form.Panel", {
      bodyPadding: 10,
      border: false,
      layout: "anchor",
      scrollable: true,
      defaults: {
        anchor: "100%",
      },
      items: [],
    });
        
    Ext.create("Ext.window.Window", {
      title: __("Edit value"),
      modal: true,
      // width: this.getEditorWidth(),
      // height: this.getEditorHeight(),
      layout: "fit",
      autoShow: true,
      items: this.formPanel,
      buttons: [{
        text: __("Cancel"),
        handler: function(){
          this.up("window").close();
        },
      }, {
        text: __("Reset"),
        scope: this,
        handler: this.resetForm,
      }, {
        text: __("Save"),
        scope: this,
        handler: function(button){
          this.request("PUT", button);
        },
      }],
    });
  },
});