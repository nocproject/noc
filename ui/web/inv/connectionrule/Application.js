//---------------------------------------------------------------------
// inv.connectionrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.connectionrule.Application");

Ext.define("NOC.inv.connectionrule.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.core.StringListField",
    "NOC.inv.connectionrule.Model",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.inv.connectionrule.Model",
  search: true,

  actions: [
    {
      title: __("Get JSON"),
      action: "json",
      glyph: NOC.glyph.file,
      resultTemplate: "JSON",
    },
  ],

  initComponent: function(){
    var me = this;

    // JSON Panel
    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/inv/connectionrule/{0}/json/",
      previewName: "Connection Rule: {0}",
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
          text: __("Builtin"),
          dataIndex: "is_builtin",
          width: 50,
          renderer: NOC.render.Bool,
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
          name: "name",
          fieldLabel: __("Name"),
          xtype: "textfield",
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
          name: "context",
          xtype: "gridfield",
          fieldLabel: __("Context"),
          columns: [
            {
              text: __("Type"),
              dataIndex: "type",
              width: 100,
              editor: "textfield",
            },
            {
              text: __("Scope"),
              dataIndex: "scope",
              width: 70,
              editor: "textfield",
            },
            {
              text: __("Reset Scopes"),
              dataIndex: "reset_scopes",
              flex: 1,
              editor: "stringlistfield",
            },
          ],
        },
        {
          name: "rules",
          xtype: "gridfield",
          fieldLabel: __("Rules"),
          columns: [
            {
              text: __("Match Type"),
              dataIndex: "match_type",
              width: 100,
              editor: "textfield",
            },
            {
              text: __("Match Connection"),
              dataIndex: "match_connection",
              width: 100,
              editor: "textfield",
            },
            {
              text: __("Scope"),
              dataIndex: "scope",
              width: 50,
              editor: "textfield",
            },
            {
              text: __("Target Type"),
              dataIndex: "target_type",
              width: 100,
              editor: "textfield",
            },
            {
              text: __("Target Number"),
              dataIndex: "target_number",
              width: 100,
              editor: "textfield",
            },
            {
              text: __("Target Connection"),
              dataIndex: "target_connection",
              width: 100,
              editor: "textfield",
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

  filters: [
    {
      title: __("By Is Builtin"),
      name: "is_builtin",
      ftype: "boolean",
    },
  ],

  //
  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
});
