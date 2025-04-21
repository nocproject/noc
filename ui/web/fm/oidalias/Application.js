//---------------------------------------------------------------------
// fm.oidalias application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.oidalias.Application");

Ext.define("NOC.fm.oidalias.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.fm.oidalias.Model",
  ],
  model: "NOC.fm.oidalias.Model",
  search: true,

  initComponent: function(){
    var me = this;
    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/fm/oidalias/{0}/json/",
      previewName: "OID Alias: {0}",
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Rewrite OID"),
          dataIndex: "rewrite_oid",
          width: 200,
        },
        {
          text: __("To OID"),
          dataIndex: "to_oid",
          width: 200,
        },
        {
          text: __("Is Builtin"),
          dataIndex: "is_builtin",
          renderer: NOC.render.Bool,
          width: 50,
          sortable: false,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
      ],
      fields: [
        {
          name: "rewrite_oid",
          xtype: "textfield",
          fieldLabel: __("Rewrite OID"),
          allowBlank: false,
          regex: /^[0-9]+(\.[0-9]+)+$/,
        },
        {
          name: "to_oid",
          xtype: "textfield",
          fieldLabel: __("To OID"),
          allowBlank: true,
          regex: /^[0-9]+(\.[0-9]+)+$/,
        },
        {
          name: "uuid",
          xtype: "displayfield",
          fieldLabel: __("UUID"),
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
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
  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
});
