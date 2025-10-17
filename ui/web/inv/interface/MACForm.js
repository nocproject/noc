//---------------------------------------------------------------------
// MAC Interfaces window
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.MACForm");

Ext.define("NOC.inv.interface.MACForm", {
  extend: "Ext.window.Window",
  requires: [
    "NOC.inv.interface.MACStore",
  ],
  autoShow: true,
  closable: true,
  maximizable: true,
  modal: true,
  width: 600,
  height: 400,
  constrain: true,

  initComponent: function(){
    var me = this;

    me.store = Ext.create("NOC.inv.interface.MACStore");
    me.store.loadData(me.config.data);
    me.objectId = me.config.objectId;
    me.interfaceName = me.config.name;

    Ext.apply(me, {
      items: [
        {
          xtype: "grid",
          store: me.store,
          scrollable: "y",
          emptyText: __("No MACs collected"),
          viewConfig: {
            enableTextSelection: true,
          },
          tbar: [
            {
              scope: me,
              text: __("Refresh"),
              glyph: NOC.glyph.refresh,
              handler: me.refresh,
            },
          ],
          columns: [
            {
              text: __("Interface"),
              dataIndex: "interfaces",
              flex: 1,
            },
            {
              text: __("MAC"),
              dataIndex: "mac",
              width: 130,
            },
            {
              text: __("VLAN"),
              dataIndex: "vlan_id",
              width: 75,
            },
            {
              text: __("type"),
              dataIndex: "type",
              width: 55,
            },
          ],
        },
      ],
    });
    me.callParent();
  },

  refresh: function(){
    var me = this;

    NOC.mrt({
      scope: me,
      params: [
        {
          id: me.objectId,
          script: "get_mac_address_table",
          args: {
            interface: me.interfaceName,
          },
        },
      ],
      errorMsg: __("Failed to get MACs"),
      cb: me.loadData,
    });
  },

  loadData: function(data, scope){
    scope.store.loadData(data);
  },
});
