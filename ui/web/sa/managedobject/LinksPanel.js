//---------------------------------------------------------------------
// sa.managed_object LinksPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.LinksPanel");

Ext.define("NOC.sa.managedobject.LinksPanel", {
  extend: "NOC.core.ApplicationPanel",
  historyHashPrefix: "links",
  alias: "widget.sa.links",
  requires: [
    "NOC.sa.managedobject.LinksStore",
  ],
  initComponent: function(){
    var me = this;

    me.currentLink = null;

    me.refreshButton = Ext.create("Ext.button.Button", {
      text: __("Refresh"),
      glyph: NOC.glyph.refresh,
      scope: me,
      handler: me.onRefresh,
    });

    me.store = Ext.create("NOC.sa.managedobject.LinksStore");
    me.grid = Ext.create("Ext.grid.Panel", {
      store: me.store,
      stateful: true,
      stateId: "sa.managedobject-links",
      autoScroll: true,
      columns: [
        {
          text: __("Local Interface"),
          dataIndex: "local_interface",
          renderer: NOC.render.Lookup("local_interface"),
        },
        {
          text: __("Local Description"),
          dataIndex: "local_description",
        },
        {
          text: __("Neighbor"),
          dataIndex: "remote_object",
          renderer: NOC.render.LookupTooltip("remote_object", "{remote_platform}"),
        },
        {
          text: __("Remote Interface"),
          dataIndex: "remote_interface",
          renderer: NOC.render.Lookup("remote_interface"),
        },
        {
          text: __("Remote Description"),
          dataIndex: "remote_description",
        },
        {
          text: __("Method"),
          dataIndex: "discovery_method",
        },
        {
          text: __("First Discovered"),
          dataIndex: "first_discovered",
        },
        {
          text: __("Last seen"),
          dataIndex: "last_seen",
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
      listeners: {
        scope: me,
        select: me.onGridSelect,
      },
    });
    Ext.apply(me, {
      items: [
        me.grid,
      ],
    });
    me.callParent();
  },

  preview: function(record){
    var me = this;
    me.callParent(arguments);
    Ext.Ajax.request({
      url: "/sa/managedobject/" + record.get("id") + "/links/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        console.log("Links data", data);
        me.grid.setTitle(record.get("name") + " links");
        me.store.loadData(data);
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  //
  onGridSelect: function(grid, record){
    var me = this;
    me.currentLink = record;
  },
  //
  onRefresh: function(){
    var me = this;
    me.preview(me.currentRecord);
  },
});
