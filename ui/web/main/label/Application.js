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
          text: __("Protected"),
          dataIndex: "is_protected",
          width: 50,
          renderer: NOC.render.Bool
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
            if (item.data.enable_serviceprofile) {
              r.push(__("Service Profile"));
            }
            if (item.data.enable_managedobject) {
              r.push(__("Managed Object"));
            }
            if (item.data.enable_managedobjectprofile) {
              r.push(__("Managed Object Profile"));
            }
            if (item.data.enable_administrativedomain) {
              r.push(__("Administrative Domain"));
            }
            if (item.data.enable_authprofile) {
              r.push(__("Auth Profile"));
            }
            if (item.data.enable_commandsnippet) {
              r.push(__("Command Snippet"));
            }
            if (item.data.enable_allocationgroup) {
              r.push(__("Allocation Group"));
            }
            if (item.data.enable_networksegment) {
              r.push(__("Network Segment"));
            }
            if (item.data.enable_object) {
              r.push(__("Object"));
            }
            if (item.data.enable_objectmodel) {
              r.push(__("Object Model"));
            }
            if (item.data.enable_platform) {
              r.push(__("Platfrom"));
            }
            if (item.data.enable_resourcegroup) {
              r.push(__("Resource Group"));
            }
            if (item.data.enable_sensorprofile) {
              r.push(__("Sensor Profile"));
            }
            if (item.data.enable_subscriber) {
              r.push(__("Subscriber"));
            }
            if (item.data.enable_subscriberprofile) {
              r.push(__("Subscriber Profile"));
            }
            if (item.data.enable_supplier) {
              r.push(__("Supplier"));
            }
            if (item.data.enable_supplierprofile) {
              r.push(__("Supplier Profile"));
            }
            if (item.data.enable_dnszone) {
              r.push(__("DNS Zone"));
            }
            if (item.data.enable_dnszonerecord) {
              r.push(__("DNS Zone Record"));
            }
            if (item.data.enable_division) {
              r.push(__("GIS Division"));
            }
            if (item.data.enable_kbentry) {
              r.push(__("KB Entry"));
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
            if (item.data.expose_managedobject) {
              r.push(__("Managed Object"));
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
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true
        },
        {
          name: "is_protected",
          xtype: "checkbox",
          boxLabel: __("Protected"),
          allowBlank: true
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
            },
            {
              name: "enable_serviceprofile",
              xtype: "checkbox",
              boxLabel: __("Service Profile")
            },
            {
              name: "enable_managedobject",
              xtype: "checkbox",
              boxLabel: __("Managed Object")
            },
            {
              name: "enable_managedobjectprofile",
              xtype: "checkbox",
              boxLabel: __("Managed Object Profile")
            },
            {
              name: "enable_administrativedomain",
              xtype: "checkbox",
              boxLabel: __("Administrative Domain")
            },
            {
              name: "enable_authprofile",
              xtype: "checkbox",
              boxLabel: __("Auth Profile")
            },
            {
              name: "enable_commandsnippet",
              xtype: "checkbox",
              boxLabel: __("Command Snippet")
            },
            {
              name: "enable_allocationgroup",
              xtype: "checkbox",
              boxLabel: __("Allocation Group")
            },
            {
              name: "enable_networksegment",
              xtype: "checkbox",
              boxLabel: __("Network Segment")
            },
            {
              name: "enable_object",
              xtype: "checkbox",
              boxLabel: __("Object")
            },
            {
              name: "enable_objectmodel",
              xtype: "checkbox",
              boxLabel: __("Object Model")
            },
            {
              name: "enable_platform",
              xtype: "checkbox",
              boxLabel: __("Platform")
            },
            {
              name: "enable_resourcegroup",
              xtype: "checkbox",
              boxLabel: __("Resource Group")
            },
            {
              name: "enable_sensorprofile",
              xtype: "checkbox",
              boxLabel: __("Sensor Profile")
            },
            {
              name: "enable_subscriber",
              xtype: "checkbox",
              boxLabel: __("Subscriber")
            },
            {
              name: "enable_subscriberprofile",
              xtype: "checkbox",
              boxLabel: __("Subscriber Profile")
            },
            {
              name: "enable_supplier",
              xtype: "checkbox",
              boxLabel: __("Supplier")
            },
            {
              name: "enable_supplierprofile",
              xtype: "checkbox",
              boxLabel: __("Supplier Profile")
            },
            {
              name: "enable_dnszone",
              xtype: "checkbox",
              boxLabel: __("DNS Zone")
            },
            {
              name: "enable_dnszonerecord",
              xtype: "checkbox",
              boxLabel: __("DNS Zone")
            },
            {
              name: "enable_division",
              xtype: "checkbox",
              boxLabel: __("GIS Division")
            },
            {
              name: "enable_kbentry",
              xtype: "checkbox",
              boxLabel: __("KB Entry")
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
            },
            {
              name: "expose_managedobject",
              xtype: "checkbox",
              boxLabel: __("Managed Object")
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
