//---------------------------------------------------------------------
// inv.configuredmap application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.configuredmap.Application");

Ext.define("NOC.inv.configuredmap.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "Ext.ux.form.GridField",
    "Ext.ux.form.StringsField",
    "NOC.core.ComboBox",
    "NOC.core.label.LabelField",
    "NOC.core.tagfield.Tagfield",
    "NOC.core.JSONPreviewII",
    "NOC.core.ListFormField",
    "NOC.inv.configuredmap.Model",
    "NOC.inv.configuredmap.LookupField",
    "NOC.core.combotree.ComboTree",
    "NOC.sa.managedobject.LookupField",
    "NOC.main.imagestore.LookupField",
    "NOC.main.ref.stencil.LookupField",
    "NOC.main.ref.topologygen.LookupField",
  ],
  model: "NOC.inv.configuredmap.Model",
  search: true,

  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/inv/configuredmap/{0}/json/",
      previewName: "Spec: {0}",
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 150,
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
          xtype: "tabpanel",
          layout: "fit",
          autoScroll: true,
          tabPosition: "left",
          tabBar: {
            tabRotation: 0,
            layout: {
              align: "stretch",
            },
          },
          anchor: "-0, -50",
          defaults: {
            autoScroll: true,
            layout: "anchor",
            textAlign: "left",
            padding: 10,
          },
          items: [
            {
              title: __("Common"),
              items: [
                {
                  name: "layout",
                  xtype: "combobox",
                  fieldLabel: __("Layout"),
                  allowBlank: false,
                  uiStyle: "medium",
                  store: [
                    ["A", "Auto"],
                    ["M", "Manual"],
                    ["FS", "Spring"],
                    ["FR", "Radial"],
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Map settings"),
                  layout: "hbox",
                  defaults: {
                    padding: 4,
                  },
                  items: [
                    {
                      name: "width",
                      xtype: "numberfield",
                      fieldLabel: __("Width"),
                      labelAlign: "top",
                      allowBlank: true,
                      minValue: 1,
                      width: 100,
                    },
                    {
                      name: "height",
                      xtype: "numberfield",
                      fieldLabel: __("Height"),
                      labelAlign: "top",
                      allowBlank: true,
                      minValue: 1,
                      width: 100,
                    },
                    {
                      name: "background_opacity",
                      xtype: "numberfield",
                      fieldLabel: __("Opacity"),
                      labelAlign: "top",
                      allowBlank: true,
                      minValue: 0,
                      maxValue: 100,
                      width: 90,
                    },
                    {
                      name: "background_image",
                      xtype: "main.imagestore.LookupField",
                      fieldLabel: __("Background Image"),
                      labelAlign: "top",
                      allowBlank: true,
                    },
                  ],
                },
                {
                  name: "add_linked_node",
                  xtype: "checkboxfield",
                  boxLabel: __("Add Linked Nodes"),
                  tooltip: __("If check - use Credential Check Rules (Service Activation -> Setup -> Credential Check Rules)<br/>" +
                                        " for suggest credential"),
                  allowBlank: true,
                  listeners: {
                    render: me.addTooltip,
                  },
                },
                {
                  name: "add_topology_links",
                  xtype: "checkboxfield",
                  boxLabel: __("Add Topology links"),
                  tooltip: __("If check - use Credential Check Rules (Service Activation -> Setup -> Credential Check Rules)<br/>" +
                                        " for suggest credential"),
                  allowBlank: true,
                  listeners: {
                    render: me.addTooltip,
                  },
                },
                {
                  name: "enable_node_portal",
                  xtype: "checkboxfield",
                  boxLabel: __("Enable Node Portal"),
                  tooltip: __("If check - use Credential Check Rules (Service Activation -> Setup -> Credential Check Rules)<br/>" +
                                        " for suggest credential"),
                  allowBlank: true,
                  listeners: {
                    render: me.addTooltip,
                  },
                },
              ],
            },
            {
              title: __("Nodes"),
              items: [
                {
                  name: "nodes",
                  xtype: "listform",
                  labelAlign: "top",
                  rows: 10,
                  items: [
                    {
                      name: "node_id",
                      xtype: "displayfield",
                      hidden: true,
                    },
                    {
                      name: "node_type",
                      xtype: "combobox",
                      fieldLabel: __("Type"),
                      allowBlank: false,
                      uiStyle: "medium",
                      store: [
                        ["objectgroup", "Group"],
                        ["objectsegment", "Segment"],
                        ["managedobject", "Managed Object"],
                        ["container", "Container"],
                        ["cpe", "CPE"],
                        ["other", "Other"],
                      ],
                      listeners: {
                        change: me.onChangeType,
                      },
                    },
                    {
                      xtype: "fieldset",
                      title: __("Reference"),
                      layout: "hbox",
                      defaults: {
                        padding: 4,
                      },
                      items: [
                        {
                          name: "resource_group",
                          xtype: "noc.core.combotree",
                          restUrl: "/inv/resourcegroup/",
                          fieldLabel: __("Resource Group"),
                          listWidth: 1,
                          listAlign: "left",
                          labelAlign: "top",
                          disabled: true,
                          width: 300,
                        },
                        {
                          xtype: "noc.core.combotree",
                          restUrl: "/inv/networksegment/",
                          name: "segment",
                          fieldLabel: __("Segment"),
                          allowBlank: true,
                          labelAlign: "top",
                          disabled: true,
                          width: 200,
                        },
                        {
                          name: "managed_object",
                          xtype: "sa.managedobject.LookupField",
                          fieldLabel: __("Managed Object"),
                          allowBlank: true,
                          labelAlign: "top",
                          disabled: true,
                          width: 200,
                          renderer: NOC.render.Lookup("managed_object"),
                        },
                        {
                          name: "container",
                          xtype: "noc.core.combotree",
                          restUrl: "/inv/container/",
                          uiStyle: "medium-combo",
                          fieldLabel: __("Container"),
                          labelAlign: "top",
                          tabIndex: 220,
                          allowBlank: true,
                          renderer: NOC.render.Lookup("container"),
                        },
                        {
                          name: "add_nested",
                          xtype: "checkbox",
                          boxLabel: __("Add nested nodes"),
                          tooltip: __("Display check state on Object Form"),
                          allowBlank: true,
                          listeners: {
                            render: me.addTooltip,
                          },
                        },
                      ],
                    },
                    {
                      xtype: "fieldset",
                      title: __("Shape"),
                      layout: "hbox",
                      defaults: {
                        padding: 4,
                      },
                      items: [
                        {
                          name: "shape",
                          xtype: "combobox",
                          fieldLabel: __("Type"),
                          labelAlign: "top",
                          allowBlank: true,
                          width: 50,
                          uiStyle: "medium",
                          store: [
                            ["stencil", "Stencil"],
                            ["rectangle", "Rectangle"],
                            ["ellipse", "Ellipse"],
                          ],
                        },
                        {
                          name: "stencil",
                          xtype: "main.ref.stencil.LookupField",
                          fieldLabel: __("Shape"),
                          labelAlign: "top",
                          width: 100,
                          allowBlank: true,
                        },
                        {
                          name: "title",
                          xtype: "textfield",
                          fieldLabel: __("Title"),
                          labelAlign: "top",
                          allowBlank: true,
                          width: 200,
                          uiStyle: "large",
                        },
                      ],
                    },
                    {
                      xtype: "fieldset",
                      title: __("Portal"),
                      layout: "hbox",
                      collapsible: true,
                      collapsed: true,
                      defaults: {
                        padding: 4,
                      },
                      items: [
                        {
                          name: "portal_generator",
                          xtype: "main.ref.topologygen.LookupField",
                          fieldLabel: __("Generator"),
                          labelAlign: "top",
                          width: 100,
                          allowBlank: true,
                        },
                        {
                          name: "map_portal",
                          xtype: "inv.configuredmap.LookupField",
                          fieldLabel: __("Configured Map"),
                          labelAlign: "top",
                          width: 100,
                          allowBlank: true,
                        },
                      ],
                    },
                  ],
                },
              ],
            },
            {
              title: __("Links"),
              items: [
                {
                  name: "links",
                  xtype: "listform",
                  labelAlign: "top",
                  rows: 10,
                  items: [
                    {
                      fieldLabel: __("Source Node"),
                      labelWidth: 100,
                      name: "source_node",
                      xtype: "core.combo",
                      autoLoadOnValue: true,
                      restUrl: function(){
                        return "/inv/configuredmap/" + me.currentRecord.id + "/nodes/";
                      },
                      width: 400,
                      allowBlank: true,
                    },
                    {
                      fieldLabel: __("Target Nodes"),
                      labelWidth: 100,
                      name: "target_nodes",
                      xtype: "core.tagfield",
                      url: function(){
                        return "/inv/configuredmap/" + me.currentRecord.id + "/nodes/";
                      },
                      width: 400,
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                  ],
                },
              ],
            },
          ],
        },
      ],
      formToolbar: [
        {
          text: __("Show Map"),
          glyph: NOC.glyph.globe,
          scope: me,
          handler: me.onShowMap,
        },
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
  onShowMap: function(){
    var me = this;
    NOC.launch("inv.map", "history", {
      args: ["configured", me.currentRecord.get("id")],
    });
  },
  onChangeType: function(field, value){
    var me = this, field_name;
    Ext.Array.each(
      me.up().query('[name/="resource_group|segment|managed_object|container"]'),
      function(field){
        field.setDisabled(value !== "other");
        field.setValue(null);
      });
    switch(value){
      case "objectgroup":
        field_name = "resource_group";
        break;
      case "objectsegment":
        field_name = "segment";
        break;
      case "managedobject":
        field_name = "managed_object";
        break;
      case "container":
        field_name = "container";
        break;
    }
    if(field_name){
      me.up().query("[name=" + field_name + "]")[0].setDisabled(false);
    }
  },
});
