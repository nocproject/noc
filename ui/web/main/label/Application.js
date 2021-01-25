//---------------------------------------------------------------------
// main.label application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.label.Application");

Ext.define("NOC.main.label.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.label.Model",
    "NOC.main.remotesystem.LookupField",
    "Ext.ux.form.ColorField"
  ],
  model: "NOC.main.label.Model",
  search: true,
  initComponent: function() {
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Label"),
          dataIndex: "name",
          width: 100,
          renderer: function(v, _x, item) {
            return NOC.render.Label({
              name: item.data.name,
              description: item.data.description || "",
              bg_color1: item.data.bg_color1 || 0,
              fg_color1: item.data.fg_color1 || 0,
              bg_color2: item.data.bg_color2 || 0,
              fg_color2: item.data.fg_color2 || 0
            });
          }
        },
        {
          text: __("Allow"),
          dataIndex: "enable_agent",
          flex: 1,
          renderer: function(_x, _y, item) {
            let r = [];
            if (item.data.enable_agent) {
              r.push(__("Agent"));
            }
            if (item.data.enable_service) {
              r.push(__("Service"));
            }
            return r.join(", ");
          }
        },
        {
          text: __("Expose"),
          dataIndex: "expose_metric",
          flex: 1,
          renderer: function(_x, _y, item) {
            let r = [];
            if (item.data.expose_metric) {
              r.push(__("Metric"));
            }
            return r.join(", ");
          }
        }
      ],
      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Label"),
          uiStyle: "medium",
          allowBlank: false
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Colors"),
          defaults: {
            padding: 4,
            labelAlign: "right"
          },
          items: [
            {
              name: "bg_color1",
              xtype: "colorfield",
              fieldLabel: __("Background"),
              allowBlank: false,
              uiStyle: "medium"
            },
            {
              name: "fg_color1",
              xtype: "colorfield",
              fieldLabel: __("Foreground"),
              allowBlank: false,
              uiStyle: "medium"
            }
          ]
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Scoped Colors"),
          defaults: {
            padding: 4,
            labelAlign: "right"
          },
          items: [
            {
              name: "bg_color2",
              xtype: "colorfield",
              fieldLabel: __("Background"),
              allowBlank: false,
              uiStyle: "medium"
            },
            {
              name: "fg_color2",
              xtype: "colorfield",
              fieldLabel: __("Foreground"),
              allowBlank: false,
              uiStyle: "medium"
            }
          ]
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Enable"),
          defaults: {
            padding: 4,
            labelAlign: "right"
          },
          items: [
            {
              name: "enable_agent",
              xtype: "checkbox",
              boxLabel: __("Agent")
            },
            {
              name: "enable_service",
              xtype: "checkbox",
              boxLabel: __("Service")
            }
          ]
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Expose"),
          defaults: {
            padding: 4,
            labelAlign: "right"
          },
          items: [
            {
              name: "expose_metric",
              xtype: "checkbox",
              boxLabel: __("Metrics")
            }
          ]
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Integration"),
          defaults: {
            padding: 4,
            labelAlign: "right"
          },
          items: [
            {
              name: "remote_system",
              xtype: "main.remotesystem.LookupField",
              fieldLabel: __("Remote System"),
              allowBlank: true
            },
            {
              name: "remote_id",
              xtype: "textfield",
              fieldLabel: __("Remote ID"),
              allowBlank: true,
              uiStyle: "medium"
            }
          ]
        }
      ]
    });
    me.callParent();
  }
});
