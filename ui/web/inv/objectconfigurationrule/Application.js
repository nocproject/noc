//---------------------------------------------------------------------
// inv.objectconfigurationrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectconfigurationrule.Application");

Ext.define("NOC.inv.objectconfigurationrule.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.core.StringListField",
    "NOC.core.tagfield.Tagfield",
    "NOC.inv.objectconfigurationrule.Model",
    "NOC.inv.objectconfigurationrule.ComboEditor",
    "NOC.inv.connectiontype.LookupField",
    "NOC.inv.protocol.LookupField",
    "NOC.cm.configurationscope.LookupField",
    "NOC.cm.configurationparam.LookupField",
    "NOC.core.label.LabelField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.inv.objectconfigurationrule.Model",
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
      restUrl: "/inv/objectconfigurationrule/{0}/json/",
      previewName: "Configuration Rule: {0}",
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
          name: "connection_rules",
          xtype: "gridfield",
          fieldLabel: __("Connection Rules"),
          columns: [
            {
              text: __("Scope"),
              dataIndex: "scope",
              editor: "cm.configurationscope.LookupField",
              width: 200,
              renderer: NOC.render.Lookup("scope"),
            },
            {
              text: __("Match Slot/Ctx"),
              dataIndex: "match_context",
              width: 100,
              editor: "textfield",
            },
            {
              text: __("Connection Type"),
              dataIndex: "match_connection_type",
              editor: "inv.connectiontype.LookupField",
              width: 200,
              renderer: NOC.render.Lookup("match_connection_type"),
            },
            {
              text: __("Protocols"),
              dataIndex: "match_protocols",
              width: 200,
              editor: {
                xtype: "inv.objectconfigurationrule.comboEditor",
                url: "/inv/protocol/lookup/",
              },
              renderer: me.comboBoxRenderer,
            },
            {
              text: __("Allow Params"),
              dataIndex: "allowed_params",
              width: 200,
              editor: {
                xtype: "inv.objectconfigurationrule.comboEditor",
                url: "/cm/configurationparam/lookup/",
              },
              renderer: me.comboBoxRenderer,
            },
            {
              text: __("Deny Params"),
              dataIndex: "deny_params",
              width: 200,
              editor: {
                xtype: "inv.objectconfigurationrule.comboEditor",
                url: "/cm/configurationparam/lookup/",
              },
              renderer: me.comboBoxRenderer,
            },
          ],
        },
        {
          name: "param_rules",
          xtype: "gridfield",
          fieldLabel: __("Param Rules"),
          columns: [
            {
              text: __("Param"),
              dataIndex: "param",
              editor: "cm.configurationparam.LookupField",
              width: 200,
              renderer: NOC.render.Lookup("param"),
              sortable: false,
            },
            {
              text: __("Scope"),
              dataIndex: "scope",
              editor: "cm.configurationscope.LookupField",
              width: 200,
              renderer: NOC.render.Lookup("scope"),
              sortable: false,
            },
            {
              text: __("Hide"),
              dataIndex: "is_hide",
              width: 30,
              renderer: NOC.render.Bool,
              sortable: false,
            },
            {
              text: __("Read Only"),
              dataIndex: "is_readonly",
              width: 30,
              renderer: NOC.render.Bool,
              sortable: false,
            },
            {
              text: __("Dependency Param"),
              dataIndex: "dependency_param",
              editor: "cm.configurationparam.LookupField",
              width: 200,
              renderer: NOC.render.Lookup("dependency_param"),
              sortable: false,
            },
            {
              text: __("Dependency Param Values"),
              dataIndex: "dependency_param_values",
              width: 100,
              editor: "textfield",
              sortable: false,
            },
            {
              text: __("Choices"),
              dataIndex: "choices",
              width: 150,
              editor: "textfield",
              sortable: false,
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
  //
  comboBoxRenderer: function(value, metaData, record){
    if(Ext.isArray(value)){
      var flag = false,
        store = metaData.column.getEditor().getStore(),
        labels = Ext.Array.map(value, function(item){
          if(Ext.isObject(item) && !item.isModel){
            flag = true;
            return item.label;
          }
          return store.findRecord("id", item).get("label");
        });
      if(flag){ // Array of object from backend transfer to array of id
        var ids = Ext.Array.map(value, function(item){
          return item.id;
        })
        record.set(metaData.column.dataIndex, ids, {dirty: false});
      }
      return labels.join(", ");
    }
    return value;
  },
});
