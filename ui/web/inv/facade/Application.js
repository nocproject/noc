//---------------------------------------------------------------------
// inv.facade application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.facade.Application");

Ext.define("NOC.inv.facade.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.core.SVGField",
    "NOC.inv.facade.Model",
  ],
  model: "NOC.inv.facade.Model",
  search: true,
  treeFilter: "category",
  filters: [
    {
      title: __("By Is Builtin"),
      name: "is_builtin",
      ftype: "boolean",
    },
  ],
  initComponent: function(){
    var me = this;
    // JSON Panel
    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/inv/facade/{0}/json/",
      previewName: "Facade: {0}",
    });
    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          width: 300,
          dataIndex: "name",
        },
        {
          text: __("Builtin"),
          width: 50,
          dataIndex: "is_builtin",
          renderer: NOC.render.Bool,
          sortable: false,
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
          name: "slots",
          xtype: "displayfield",
          fieldLabel: __("Slots"),
          allowBlank: true,
        },
        {
          xtype: "svgfield",
          name: "data",
          fieldLabel: __("Image"),
          allowBlank: false,
          listeners: {
            scope: me,
            download: me.onDownload,
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
  //
  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
  //
  onDownload: function(field, data){
    var name = this.form.getValues().name;
    if(Ext.isEmpty(name)){
      name = "image";
    }
    name = name.split("|")[name.split("|").length - 1] || "image";
    field.downloadFile(name + ".svg", data);
  },
});
