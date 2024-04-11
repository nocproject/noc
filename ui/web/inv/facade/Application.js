//---------------------------------------------------------------------
// inv.facade application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.facade.Application");

Ext.define("NOC.inv.facade.Application", {
  extend: "NOC.core.ModelApplication",
  requires: ["NOC.inv.facade.Model", "NOC.core.SVGField"],
  model: "NOC.inv.facade.Model",
  search: true,
  treeFilter: "category",
  initComponent: function () {
    var me = this;
    // JSON Panel
    me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
      app: me,
      restUrl: new Ext.XTemplate("/inv/facade/{id}/json/"),
      previewName: new Ext.XTemplate("Facade: {name}"),
    });
    me.ITEM_JSON = me.registerItem(me.jsonPanel);
    //
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          width: 300,
          dataIndex: "name",
        },
        {
          text: __("Description"),
          flex: 1,
          dataIndex: "description",
        },
      ],
      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
        },
        {
          name: "uuid",
          xtype: "displayfield",
          fieldLabel: __("UUID"),
          allowBlank: false,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          xtype: "svgfield",
          name: "data",
          fieldLabel: __("Image"),
          allowBlank: false,
        },
      ],
      formToolbar: [
        {
          text: __("JSON"),
          glyph: NOC.glyph.file,
          tooltip: __("Show JSON"),
          hasAccess: NOC.hasPermission("read"),
          scope: me,
          handler: me.onJSON,
        },
      ],
    });
    me.callParent();
  },
  //
  onJSON: function () {
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord);
  },
});
