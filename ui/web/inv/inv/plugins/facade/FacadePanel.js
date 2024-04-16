//---------------------------------------------------------------------
// inv.inv Facade panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.facade.FacadePanel");

Ext.define("NOC.inv.inv.plugins.facade.FacadePanel", {
  extend: "Ext.panel.Panel",
  requires: [],
  title: __("Facade"),
  closable: false,
  scrollable: true,

  initComponent: function () {
    var me = this;

    me.facadeViewPanel = Ext.create("Ext.container.Container", {
      scrollable: true,
      region: "center",
    });
    Ext.apply(me, {
      items: [me.facadeViewPanel],
    });
    me.callParent();
  },
  //
  preview: function (data) {
    var me = this;
    Ext.each(data.views, function(view) {
      me.facadeViewPanel.add([
        {
          xtype: "component",
          html: Ext.String.format("<h2 style='padding-left: 10px;'>{0}</h2>", view.name),
        },
        {
          xtype: "image",
          src: view.src,
          title: view.name,
          padding: 5,
        }
      ]);
    });
  },
});
