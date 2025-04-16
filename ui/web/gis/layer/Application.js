//---------------------------------------------------------------------
// gis.layer application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.layer.Application");

Ext.define("NOC.gis.layer.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.gis.layer.Model",
    "Ext.ux.form.ColorField",
  ],
  model: "NOC.gis.layer.Model",
  search: true,
  initComponent: function(){
    var me = this;

    // JSON Panel
    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/gis/layer/{0}/json/",
      previewName: "Layer: {0}",
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
          text: __("Code"),
          dataIndex: "code",
          width: 100,
        },
        {
          text: __("Builtin"),
          dataIndex: "is_builtin",
          renderer: NOC.render.Bool,
          width: 50,
        },
        {
          text: __("zIndex"),
          dataIndex: "zindex",
          width: 50,
          align: "right",
        },
        {
          text: __("Min Zoom"),
          dataIndex: "min_zoom",
          width: 50,
          align: "right",
        },
        {
          text: __("Max Zoom"),
          dataIndex: "max_zoom",
          width: 50,
          align: "right",
        },
        {
          text: __("Def. Zoom"),
          dataIndex: "default_zoom",
          width: 50,
          align: "right",
        },
        {
          text: __("Color"),
          dataIndex: "stroke_color",
          width: 50,
          renderer: me.renderStyle,
        },
      ],
      fields: [
        {
          xtype: "textfield",
          name: "name",
          fieldLabel: __("Name"),
          allowBlank: false,
        },
        {
          xtype: "textfield",
          name: "code",
          fieldLabel: __("Code"),
          allowBlank: false,
        },
        {
          xtype: "displayfield",
          name: "uuid",
          fieldLabel: __("UUID"),
        },
        {
          xtype: "textarea",
          name: "description",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          xtype: "numberfield",
          name: "zindex",
          fieldLabel: __("zIndex"),
          minValue: 0,
        },
        {
          xtype: "fieldset",
          title: __("Zoom"),
          layout: "hbox",
          items: [
            {
              xtype: "numberfield",
              name: "min_zoom",
              fieldLabel: __("Min"),
              minValue: 0,
              maxValue: 19,
            },
            {
              xtype: "numberfield",
              name: "max_zoom",
              fieldLabel: __("Max"),
              minValue: 0,
              maxValue: 19,
            },
            {
              xtype: "numberfield",
              name: "default_zoom",
              fieldLabel: __("Default"),
              minValue: 0,
              maxValue: 19,
            },
          ],
        },
        {
          xtype: "fieldset",
          title: __("Style"),
          items: [
            {
              name: "stroke_color",
              xtype: "colorfield",
              fieldLabel: __("Stroke Color"),
              allowBlank: false,
            },
            {
              name: "fill_color",
              xtype: "colorfield",
              fieldLabel: __("Fill Color"),
              allowBlank: false,
            },
            {
              name: "stroke_width",
              xtype: "numberfield",
              fieldLabel: __("Stroke Width"),
              allowBlank: true,
            },
          ],
        },
        {
          xtype: "fieldset",
          title: __("Point Style"),
          items: [
            {
              name: "point_radius",
              xtype: "numberfield",
              fieldLabel: __("Point Radius"),
              minValue: 0,
              allowBlank: true,
            },
            {
              name: "point_graphic",
              xtype: "combobox",
              fieldLabel: __("Graphic"),
              allowBlank: true,
              store: [
                ["circle", "circle"],
                ["triangle", "triangle"],
                ["cross", "cross"],
                ["x", "x"],
                ["square", "square"],
                ["star", "star"],
                ["diamond", "diamond"],
                ["antenna", "antenna"],
                ["flag", "flag"],
              ],
            },
          ],
        },
        {
          xtype: "fieldset",
          title: __("Line Style"),
          items: [
            {
              name: "stroke_dashstyle",
              xtype: "combobox",
              fieldLabel: __("Line Style"),
              allowBlank: true,
              store: [
                ["solid", "solid"],
                ["dash", "dash"],
                ["dashdot", "dashdot"],
                ["longdash", "longdash"],
                ["longdashdot", "longdashdot"],
              ],
            },
          ],
        },
        {
          xtype: "fieldset",
          title: __("Text Style"),
          items: [
            {
              name: "show_labels",
              xtype: "checkboxfield",
              boxLabel: __("Show Labels"),
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
  renderStyle: function(value, meta, record){
    return "<span style='padding: 2px; border: 1px solid #" + record.get("stroke_color") + "; background-color: #" + record.get("fill_color") + "'>&nbsp;&nbsp;&nbsp;&nbsp;</span>";
  },
  //
  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
});
