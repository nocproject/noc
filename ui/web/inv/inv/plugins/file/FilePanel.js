//---------------------------------------------------------------------
// inv.inv Comment panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.file.FilePanel");

Ext.define("NOC.inv.inv.plugins.file.FilePanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.file.FileModel",
  ],
  title: __("Files"),
  closable: false,
  layout: "fit",
  autoScroll: true,

  initComponent: function(){
    var me = this;

    me.store = Ext.create("Ext.data.Store", {
      model: "NOC.inv.inv.plugins.file.FileModel",
      autoLoad: false,
    });

    me.uploadButton = Ext.create("Ext.button.Button", {
      text: __("Upload"),
      glyph: NOC.glyph.upload,
      scope: me,
      handler: me.onUpload,
    });

    me.deleteButton = Ext.create("Ext.button.Button", {
      text: __("Delete"),
      glyph: NOC.glyph.times,
      scope: me,
      handler: me.onDelete,
    });

    me.grid = Ext.create("Ext.grid.Panel", {
      store: me.store,
      autoScroll: true,
      stateful: true,
      stateId: "inv.inv-file-grid",
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 200,
        },
        {
          text: __("Date"),
          dataIndex: "ts",
          width: 120,
          renderer: NOC.render.DateTime,
        },
        {
          text: __("Size"),
          dataIndex: "size",
          width: 50,
          renderer: NOC.render.Size,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
      ],
      listeners: {
        scope: me,
        select: me.onSelect,
        celldblclick: me.onDblClick,
      },
    });

    // Grids
    Ext.apply(me, {
      items: [me.grid],
      dockedItems: [{
        xtype: "toolbar",
        dock: "top",
        items: [
          me.uploadButton,
          "-",
          me.deleteButton,
        ],
      }],
    });
    me.callParent();
  },
  //
  preview: function(data){
    var me = this;
    me.currentId = data.id;
    me.store.loadData(data.files);
    me.deleteButton.setDisabled(me.grid.getSelectionModel().getSelection().length == 0);
  },
  //
  onUpload: function(){
    var me = this;
    Ext.create("NOC.inv.inv.plugins.file.UploadForm", {app: me});
  },
  //
  refresh: function(){
    var me = this;
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/file/",
      method: "GET",
      scope: me,
      success: function(response){
        me.preview(Ext.decode(response.responseText));
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  //
  onDelete: function(){
    var me = this,
      sm = me.grid.getSelectionModel(),
      sel = sm.getSelection();
    if(sel.length === 0){
      return
    }
    Ext.Msg.show({
      title: "Remove file '" + sel[0].get("name") + "'?",
      msg: "Would you like to remove file? Once removed operation cannot be undone",
      buttons: Ext.Msg.YESNO,
      glyph: NOC.glyph.question_circle,
      fn: function(rec){
        if(rec === "yes"){
          Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/file/" + sel[0].get("id") + "/",
            method: "DELETE",
            scope: me,
            success: function(){
              me.refresh();
            },
            failure: function(){
              NOC.error(__("Failed to delete file"));
            },
          });
        }
      },
    });
  },
  //
  onSelect: function(){
    var me = this;
    me.deleteButton.setDisabled(me.grid.getSelectionModel().getSelection().length == 0);
  },
  //
  onDblClick: function(grid, td, cellIndex, record){
    var me = this;
    window.open("/inv/inv/" + me.currentId + "/plugin/file/" + record.get("id") + "/");
  },
});
