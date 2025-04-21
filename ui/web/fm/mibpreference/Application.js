//---------------------------------------------------------------------
// fm.mibpreference application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.mibpreference.Application");

Ext.define("NOC.fm.mibpreference.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.fm.mibpreference.Model",
  ],
  model: "NOC.fm.mibpreference.Model",
  search: true,

  initComponent: function(){
    var me = this;
    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/fm/mibpreference/{0}/json/",
      previewName: "MIB Preference: {0}",
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);


    Ext.apply(me, {
      columns: [
        {
          text: __("MIB"),
          dataIndex: "mib",
          width: 300,
        },
        {
          text: __("Pref."),
          dataIndex: "preference",
          width: 100,
        },
        {
          text: __("Builtin"),
          dataIndex: "is_builtin",
          renderer: NOC.render.Bool,
          width: 50,
          sortable: false,
        },
      ],
      fields: [
        {
          name: "mib",
          xtype: "textfield",
          fieldLabel: __("MIB"),
          allowBlank: false,
        },
        {
          name: "uuid",
          xtype: "displayfield",
          fieldLabel: __("UUID"),
        },
        {
          name: "preference",
          xtype: "numberfield",
          fieldLabel: __("Preference"),
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
  onJSON: function(){
    var me = this,
      record = new Ext.data.Model({
        id: me.currentRecord.get("id"),
        name: me.currentRecord.get("mib"),
      });
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(record, me.ITEM_FORM);
  },
});
