//---------------------------------------------------------------------
// main.glyph application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.glyph.Application");

Ext.define("NOC.main.glyph.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.main.glyph.Model",
    "NOC.main.font.LookupField",
  ],
  model: "NOC.main.glyph.Model",
  search: true,

  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/main/font/{0}/json/",
      previewName: "Font: {0}",
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 200,
        },
        {
          text: __("Font"),
          dataIndex: "font",
          renderer: NOC.render.Lookup("font"),
          width: 100,
        },
        {
          text: __("Glyph"),
          dataIndex: "code",
          width: 100,
          renderer: function(value, meta, record){
            return "<span style='font-family: " + record.get("font__label") + "'>&#" + value + ";</span>";
          },
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "large",
        },
        {
          name: "uuid",
          xtype: "displayfield",
          fieldLabel: __("UUID"),
          allowBlank: true,
        },
        {
          itemId: "font",
          name: "font",
          xtype: "main.font.LookupField",
          fieldLabel: __("Font"),
          allowBlank: false,
        },
        {
          name: "code",
          xtype: "textfield",
          fieldLabel: __("Code (HEX)"),
          emptyText: __("Enter HEX number"),
          allowBlank: false,
          regex: /^[0-9a-fA-F]+$/,
          invalidText: __("Invalid HEX format"),
          valueToRaw: function(value){
            return Ext.util.Format.hex(value);
          },
          rawToValue: function(value){
            if(this.regex.test(value)){
              return parseInt(value, 16);
            }
            return value;
          },
          listeners: {
            change: function(field, newValue){
              field.up().queryById("preview").setValue(newValue);
            },
          },
          uiStyle: "medium",
        },
        {
          itemId: "preview",
          xtype: "displayfield",
          uiStyle: "small",
          fieldLabel: __("Preview"),
          renderer: function(value, field){
            var fontName = field.up().queryById("font").getRawValue();
            if(fontName){
              return "<span style='font-family: " + fontName + ";'>&#" + value + "</span>";
            }
          },
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

  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
});
