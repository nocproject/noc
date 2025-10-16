//---------------------------------------------------------------------
// sa.managedobject CPEPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.CPEPanel");

Ext.define("NOC.sa.managedobject.CPEPanel", {
  extend: "NOC.core.ApplicationPanel",
  app: null,
  autoScroll: true,
  historyHashPrefix: "cpe",

  initComponent: function(){
    var me = this;

    me.currentObject = null;

    me.refreshButton = Ext.create("Ext.button.Button", {
      text: __("Refresh"),
      glyph: NOC.glyph.refresh,
      scope: me,
      handler: me.onRefresh,
    });

    // Create stores
    me.store = Ext.create("Ext.data.Store", {
      model: null,
      data: [],
      fields: [
        {
          name: "address",
          type: "string",
        },
        {
          name: "description",
          type: "string",
        },
        {
          name: "global_id",
          type: "string",
        },
        {
          name: "interface",
          type: "string",
        },
        {
          name: "local_id",
          type: "string",
        },
        {
          name: "location",
          type: "string",
        },
        {
          name: "mac",
          type: "string",
        },
        {
          name: "model",
          type: "string",
        },
        {
          name: "name",
          type: "string",
        },
        {
          name: "serial",
          type: "string",
        },
        {
          name: "status",
          type: "string",
        },
        {
          name: "version",
          type: "string",
        },
      ],
    });
    me.grid = Ext.create(
      {
        xtype: "gridpanel",
        border: false,
        autoScroll: true,
        stateful: true,
        stateId: "sa.managedobject-cpe-grid",
        store: me.store,
        columns: [
          {
            text: __("Address"),
            dataIndex: "address",
          },
          {
            text: __("Description"),
            dataIndex: "description",
          },
          {
            text: __("Global Id"),
            dataIndex: "global_id",
          },
          {
            text: __("Interface"),
            dataIndex: "interface",
          },
          {
            text: __("Loca Id"),
            dataIndex: "local_id",
          },
          {
            text: __("Location"),
            dataIndex: "location",
          },
          {
            text: __("Mac"),
            dataIndex: "mac",
          },
          {
            text: __("Model"),
            dataIndex: "model",
          },
          {
            text: __("Name"),
            dataIndex: "name",
          },
          {
            text: __("Serial"),
            dataIndex: "serial",
          },
          {
            text: __("Status"),
            dataIndex: "status",
          },
          {
            text: __("Version"),
            dataIndex: "version",
          },
        ],
      },
    );
    //
    Ext.apply(me, {
      items: [
        me.grid,
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
    me.callParent();
  },
  //
  preview: function(record){
    var me = this;
    me.callParent(arguments);
    me.setTitle(record.get("name") + " CPE");
    Ext.Ajax.request({
      url: "/sa/managedobject/" + record.get("id") + "/cpe/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        // Load data
        me.store.loadData(data.cpe || []);
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
});
