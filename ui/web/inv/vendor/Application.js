//---------------------------------------------------------------------
// inv.vendor application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.vendor.Application");

Ext.define("NOC.inv.vendor.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.core.TagsField",
    "NOC.inv.vendor.Model",
  ],
  model: "NOC.inv.vendor.Model",
  search: true,

  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
      width: 150,
    },
    {
      text: __("Full Name"),
      dataIndex: "full_name",
      width: 200,
    },
    {
      text: __("Code"),
      dataIndex: "code",
      width: 200,
    },
    {
      text: __("Site"),
      dataIndex: "site",
      flex: 1,
      renderer: NOC.render.URL,
    },
    {
      text: __("Builtin"),
      dataIndex: "is_builtin",
      width: 30,
      renderer: NOC.render.Bool,
      sortable: false,
    },
  ],
  fields: [
    {
      name: "name",
      xtype: "textfield",
      fieldLabel: __("Name"),
      allowBlank: false,
      uiStyle: "medium",
    },
    {
      name: "full_name",
      xtype: "textfield",
      fieldLabel: __("Full Name"),
      allowBlank: false,
      uiStyle: "medium",
    },
    {
      name: "uuid",
      xtype: "displayfield",
      fieldLabel: __("UUID"),
    },
    {
      name: "code",
      xtype: "tagsfield",
      fieldLabel: __("Code"),
      allowBlank: false,
    },
    {
      name: "site",
      xtype: "textfield",
      fieldLabel: __("Site"),
      allowBlank: false,
    },
  ],
  //
  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/inv/vendor/{0}/json/",
      previewName: "Vendor: {0}",
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);
    Ext.apply(me, {
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
  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
});
