//---------------------------------------------------------------------
// fm.mib application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.mib.Application");

Ext.define("NOC.fm.mib.Application", {
  extend: "NOC.core.ModelApplication",
  model: "NOC.fm.mib.Model",
  search: true,
  requires: [
    "NOC.core.Preview",
    "NOC.fm.mib.MIBUpload",
  ],
  columns: [
    {
      text: __("MIB"),
      dataIndex: "name",
      flex: 1,
    },
    {
      text: __("Last Updated"),
      dataIndex: "last_updated",
      width: 100,
    },
  ],

  preview: {
    xtype: "NOC.core.Preview",
    previewName: new Ext.XTemplate("MIB: {name}"),
    restUrl: new Ext.XTemplate("/fm/mib/{id}/text/"),
  },

  createForm: function(){
    var me = this;
    //
    me.toolbarIdField = Ext.create("Ext.form.field.Display", {
      fieldLabel: __("ID"),
      labelWidth: 15,
    });
    //
    me.closeButton = Ext.create("Ext.button.Button", {
      text: __("Close"),
      glyph: NOC.glyph.arrow_left,
      scope: me,
      handler: me.showGrid,
    });
    //
    me.previewButton = Ext.create("Ext.button.Button", {
      text: __("View"),
      glyph: NOC.glyph.file,
      scope: me,
      handler: me.onPreview,
    });
    //
    me.treeStore = Ext.create("Ext.data.TreeStore", {
      fields: ["oid", "name", "description", "syntax"],
      root: {
        expanded: false,
        children: [],
      },
    });
    //
    return Ext.create("Ext.tree.Panel", {
      store: me.treeStore,
      rootVisible: true,
      useArrows: true,
      columns: [
        {
          xtype: "treecolumn",
          text: __("OID"),
          dataIndex: "oid",
          width: 300,
        },
        {
          text: __("Name"),
          dataIndex: "name",
          width: 300,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
          xtype: "templatecolumn",
          tpl: "<pre>{description}</pre>",
        },
        {
          text: __("Syntax"),
          dataIndex: "syntax",
          width: 200,
          xtype: "templatecolumn",
          tpl: "<pre>{syntax}</pre>",
        },
      ],
      dockedItems: [{
        xtype: "toolbar",
        dock: "top",
        items: [
          me.closeButton,
          "->",
          me.toolbarIdField,
        ],
      }],
    });
  },
  //
  editRecord: function(record){
    var me = this;
    me.currentRecord = record;
    me.setFormTitle(me.changeTitle);
    // me.setFormId(me.currentRecord.get(me.idField));
    // Show edit form
    me.showForm();
  },
  //
  showForm: function(){
    var me = this,
      form = me.getRegisteredItems()[me.ITEM_FORM];
    form.setTitle("MIB: " + me.currentRecord.get("name"));
    me.callParent();
    me.loadMIB();
  },
  //
  loadMIB: function(){
    var me = this;
    Ext.Ajax.request({
      url: "/fm/mib/" + me.currentRecord.get("id") + "/data/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        me.treeStore.setRootNode(data);
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  //
  onNewRecord: function(){
    var me = this;
    Ext.create("NOC.fm.mib.MIBUpload", {
      app: me,
    });
  },
});
