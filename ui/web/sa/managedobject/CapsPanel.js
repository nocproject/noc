//---------------------------------------------------------------------
// sa.managedobject CapsPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.CapsPanel");

Ext.define("NOC.sa.managedobject.CapsPanel", {
  extend: "NOC.core.ApplicationPanel",
  requires: [
  ],
  autoScroll: true,

  initComponent: function(){
    var me = this;

    me.refreshButton = Ext.create("Ext.button.Button", {
      text: __("Refresh"),
      glyph: NOC.glyph.refresh,
      scope: me,
      handler: me.onRefresh,
    });

    me.store = Ext.create("Ext.data.Store", {
      model: "NOC.fm.alarm.Model",
      fields: ["capability", "description"],
      data: [],
    });

    me.grid = Ext.create("Ext.grid.Panel", {
      store: me.store,
      stateful: true,
      stateId: "sa.managedobject-caps",
      columns: [
        {
          text: __("Capability"),
          dataIndex: "capability",
          width: 300,
        },
        {
          text: __("Value"),
          dataIndex: "value",
          width: 100,
          renderer: me.renderValue,
        },
        {
          text: __("Source"),
          dataIndex: "source",
          width: 100,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
      ],
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          items: [
            me.getCloseButton(),
            me.refreshButton,
          ],
        },
      ],
    });
    Ext.apply(me, {
      items: [
        me.grid,
      ],
    });
    me.callParent();
  },
  //
  preview: function(record){
    var me = this;
    me.callParent(arguments);
    me.setTitle(record.get("name") + " capabilities");
    Ext.Ajax.request({
      url: "/sa/managedobject/" + me.currentRecord.get("id") + "/caps/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        me.store.loadData(data);
      },
      failure: function(){
        NOC.error(__("Failed to load data"));
      },
    });
  },
  //
  onRefresh: function(){
    var me = this;
    me.preview(me.currentRecord);
  },
  //
  renderValue: function(v){
    if((v === true) || (v === false)){
      return NOC.render.Bool(v);
    } else{
      return v;
    }
  },
});
