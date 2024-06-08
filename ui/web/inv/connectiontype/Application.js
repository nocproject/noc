//---------------------------------------------------------------------
// inv.connectiontype application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.connectiontype.Application");

Ext.define("NOC.inv.connectiontype.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreview",
    "NOC.core.TemplatePreview",
    "Ext.ux.form.ModelDataField",
    "NOC.inv.connectiontype.LookupField",
    "NOC.inv.facade.LookupField",
  ],
  model: "NOC.inv.connectiontype.Model",
  search: true,
  treeFilter: "category",
  filters: [
    {
      title: __("By Is Builtin"),
      name: "is_builtin",
      ftype: "boolean",
    },
  ],
  //
  initComponent: function () {
    var me = this;
    // JSON Panel
    me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
      app: me,
      restUrl: new Ext.XTemplate("/inv/connectiontype/{id}/json/"),
      previewName: new Ext.XTemplate("Connection Type: {name}"),
    });
    me.ITEM_JSON = me.registerItem(me.jsonPanel);
    // Test panel
    me.testPanel = Ext.create("NOC.core.TemplatePreview", {
      app: me,
      previewName: new Ext.XTemplate("Compatible connections for {name}"),
      template: new Ext.XTemplate(
        '<div class="noc-tp">\n    <h1>Possible connections for type {name}</h1>\n    <table border="1">\n        <tpl foreach="data">\n            <tr>\n                <th colspan="4">Gender \'{gender}\' can be connected to:</th>\n            </tr>\n            <tr>\n                <th>Gender</th>\n                <th>Connection Type</th>\n                <th>Reason</th>\n                <th>Description</th>\n            </tr>\n            <tpl foreach="records">\n                <tr>\n                    <td>{gender}</td>\n                    <td>{name}</td>\n                    <td>{reason}</td>\n                    <td>{description}</td>\n                </tr>\n            </tpl>\n        </tpl>\n    </table>\n</div>',
      ),
    });
    me.ITEM_TEST = me.registerItem(me.testPanel);
    //
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
          text: __("Genders"),
          width: 50,
          dataIndex: "genders",
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
          name: "extend",
          xtype: "inv.connectiontype.LookupField",
          fieldLabel: __("Extend"),
          allowBlank: true,
        },
        {
          name: "genders",
          xtype: "combobox",
          fieldLabel: __("Genders"),
          store: [
            ["s", "Genderless"],
            ["ss", "Genderless, 2 or more"],
            ["m", "Only male"],
            ["f", "Only female"],
            ["mmf", "Males/Female"],
            ["mf", "Male/Female"],
            ["mff", "Male/Females"],
          ],
          allowBlank: false,
          uiStyle: "medium",
        },
        {
          name: "male_facade",
          xtype: "inv.facade.LookupField",
          fieldLabel: __("Male Facade"),
          allowBlank: true,
        },
        {
          name: "female_facade",
          xtype: "inv.facade.LookupField",
          fieldLabel: __("Female Facade"),
          allowBlank: true,
        },
        // {
        //   name: "data",
        //   xtype: "modeldatafield",
        //   fieldLabel: __("Model Data"),
        // },
        {
          name: "data",
          fieldLabel: __("Data"),
          xtype: "gridfield",
          allowBlank: true,
          columns: [
            {
              text: __("Interface"),
              dataIndex: "interface",
              editor: {
                xtype: "inv.modelinterface.LookupField",
                forceSelection: true,
                valueField: "label",
              },
            },
            {
              text: __("Key"),
              dataIndex: "attr",
              editor: "textfield",
            },
            {
              text: __("Value"),
              dataIndex: "value",
              editor: "textfield",
            }
          ]
        },
        {
          name: "c_group",
          xtype: "stringlistfield",
          fieldLabel: __("Compatible groups"),
        },
        {
          name: "matchers",
          xtype: "gridfield",
          fieldLabel: __("Matchers"),
          columns: [
            {
              text: __("Scope"),
              dataIndex: "scope",
              editor: "textfield",
              width: 100,
            },
            {
              text: __("Protocol"),
              dataIndex: "protocol",
              editor: "textfield",
              flex: 1,
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
        {
          text: __("Test"),
          glyph: NOC.glyph.question,
          tooltip: __("Test compatible types"),
          hasAccess: NOC.hasPermission("read"),
          scope: me,
          handler: me.onTest,
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
  //
  onTest: function () {
    var me = this;
    Ext.Ajax.request({
      url: "/inv/connectiontype/" + me.currentRecord.get("id") + "/compatible/",
      method: "GET",
      scope: me,
      success: function (response) {
        var data = Ext.decode(response.responseText);
        me.showItem(me.ITEM_TEST).preview(me.currentRecord, { data: data });
      },
      failure: function () {
        NOC.error(__("Failed to get data"));
      },
    });
  },
});
