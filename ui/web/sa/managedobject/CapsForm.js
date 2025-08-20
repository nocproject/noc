//---------------------------------------------------------------------
// Capabilities window
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.CapsForm");

Ext.define("NOC.sa.managedobject.CapsForm", {
  extend: "Ext.Window",
  requires: [
    "NOC.core.plugins.DynamicModalEditing",
    "NOC.core.InlineModelStore",
    "NOC.inv.interface.CapabilitiesModel",
    "NOC.core.InlineGrid",
  ],
  autoShow: true,
  closable: true,
  maximizable: true,
  modal: true,
  scrollable: true,
  width: "50%",
  height: "30%",
  layout: "fit",

  initComponent: function(){
    Ext.apply(this, {
      items: [
        {
          xtype: "inlinegrid",
          title: __("Capabilities"),
          collapsible: false,
          collapsed: false,
          itemId: "sa-mo-caps-inline",
          store: Ext.create("NOC.core.InlineModelStore", {
            model: "NOC.inv.interface.CapabilitiesModel",
          }),
          readOnly: true,
          bbar: {},
          plugins: [
            {
              ptype: "dynamicmodalediting",
              listeners: {
                canceledit: "onCancelEdit",
              },
            },
          ],
          columns: [
            {
              text: __("Capability"),
              dataIndex: "capability",
              width: 200,
            },
            {
              text: __("Value"),
              dataIndex: "value",
              useModalEditor: true,
              urlPrefix: "/inv/interface",
            },
            {
              text: __("Scope"),
              dataIndex: "scope",
              width: 80,
            },
            {
              text: __("Source"),
              dataIndex: "source",
              width: 70,
            },
            {
              text: __("Description"),
              dataIndex: "description",
              flex: 1,
            },
          ],
        },
      ],
    });
    this.callParent();
    this.loadStore(this.rowId);
  },
  
  loadStore: function(id){
    let store = this.down("[itemId=sa-mo-caps-inline]").getStore();
    store.setParent(id);
    this.app.mask(__("Loading capabilities..."));
    store.load({
      scope: this.app,
      callback: function(records, operation, success){
        this.unmask();
        if(!success){
          NOC.error(__("Failed to load capabilities"));
        }
      },
    });
  },
});