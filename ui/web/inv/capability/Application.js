//---------------------------------------------------------------------
// inv.capability application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.capability.Application");

Ext.define("NOC.inv.capability.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.inv.capability.Model",
  ],
  model: "NOC.inv.capability.Model",
  search: true,
  treeFilter: "category",

  initComponent: function(){
    var me = this;

    // JSON Panel
    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/inv/capability/{0}/json/",
      previewName: "Capability: {0}",
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
          allowBlank: true,
        },
        {
          name: "type",
          xtype: "combobox",
          fieldLabel: __("Type"),
          store: [
            ["bool", "Boolean"],
            ["str", "String"],
            ["int", "Integer"],
            ["float", "Float"],
          ],
        },
        {
          name: "allow_manual",
          xtype: "checkbox",
          boxLabel: __("Allowing Manual Editor"),
        },
        {
          name: "multi",
          xtype: "checkbox",
          boxLabel: __("Allow multiple values (List)"),
        },
        {
          name: "values",
          xtype: "dictfield",
          fieldLabel: __("Values"),
        },
        {
          name: "card_template",
          xtype: "textfield",
          fieldLabel: __("Card Template"),
          allowBlank: true,
        },
        {
          xtype: "container",
          layout: "hbox",
          defaults: {
            padding: "0 8 0 0",
          },
          items: [
            {
              name: "agent_collector",
              xtype: "combobox",
              uiStyle: "medium",
              fieldLabel: __("Agent Collector"),
              store: [
                ["cpu", "CPU"],
                ["memory", "Memory"],
                ["dns", "DNS"],
                ["fs", "FS"],
                ["http", "HTTP"],
                ["network", "Network"],
                ["twamp_reflector", "TWAMP Reflector"],
                ["twamp_sender", "TWAMP Sender"],
                ["block_io", "Block IO"],
              ],
            },
            {
              name: "agent_param",
              xtype: "textfield",
              uiStyle: "medium",
              fieldLabel: __("Agent Param"),
              allowBlank: true,
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
