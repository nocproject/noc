//---------------------------------------------------------------------
// inv.modelinterface application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.modelinterface.Application");

Ext.define("NOC.inv.modelinterface.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.inv.modelinterface.Model",
  search: true,
  //
  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/inv/modelinterface/{0}/json/",
      previewName: "Model Interface: {0}",
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
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
        },
        {
          name: "attrs",
          xtype: "gridfield",
          fieldLabel: __("Attrs"),
          columns: [
            {
              text: __("Name"),
              dataIndex: "name",
              editor: "textfield",
            },
            {
              text: __("Type"),
              dataIndex: "type",
              editor: {
                xtype: "combobox",
                store: [
                  "str", "strlist",
                  "int", "float", "bool",
                  "objectid", "ref",
                ],
                forceSelection: true,
              },
            },
            {
              text: __("Description"),
              dataIndex: "description",
              editor: "textfield",
              flex: 1,
            },
            {
              text: __("Req."),
              dataIndex: "required",
              editor: "checkboxfield",
              width: 30,
              renderer: NOC.render.Bool,
            },
            {
              text: __("Const."),
              dataIndex: "is_const",
              editor: "checkboxfield",
              width: 30,
              renderer: NOC.render.Bool,
            },
          ],
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
