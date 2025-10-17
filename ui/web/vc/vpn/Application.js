//---------------------------------------------------------------------
// vc.vpn application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vpn.Application");

Ext.define("NOC.vc.vpn.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.label.LabelField",
    "NOC.core.StateField",
    "NOC.vc.vpn.Model",
    "NOC.vc.vpnprofile.LookupField",
    "NOC.main.remotesystem.LookupField",
    "NOC.project.project.LookupField",
    "NOC.sa.managedobject.LookupField",
    "NOC.vc.vpn.LookupField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.vc.vpn.Model",
  rowClassField: "row_class",
  search: true,
  helpId: "reference-vpn",

  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 150,
        },
        {
          text: __("Profile"),
          dataIndex: "profile",
          width: 150,
          renderer: NOC.render.Lookup("profile"),
        },
        {
          text: __("State"),
          dataIndex: "state",
          width: 150,
          renderer: NOC.render.Lookup("state"),
        },
        {
          text: __("Project"),
          dataIndex: "project",
          width: 150,
          renderer: NOC.render.Lookup("project"),
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "medium",
        },
        {
          name: "profile",
          xtype: "vc.vpnprofile.LookupField",
          fieldLabel: __("Profile"),
          allowBlank: false,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "state",
          xtype: "statefield",
          fieldLabel: __("State"),
          allowBlank: true,
        },
        {
          name: "parent",
          xtype: "vc.vpn.LookupField",
          fieldLabel: __("Parent"),
          allowBlank: true,
        },
        {
          name: "project",
          xtype: "project.project.LookupField",
          fieldLabel: __("Project"),
          allowBlank: true,
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Integration"),
          defaults: {
            padding: 4,
            labelAlign: "right",
          },
          items: [
            {
              name: "remote_system",
              xtype: "main.remotesystem.LookupField",
              fieldLabel: __("Remote System"),
              allowBlank: true,
            },
            {
              name: "remote_id",
              xtype: "textfield",
              fieldLabel: __("Remote ID"),
              allowBlank: true,
              uiStyle: "medium",
            },
            {
              name: "bi_id",
              xtype: "displayfield",
              fieldLabel: __("BI ID"),
              allowBlank: true,
              uiStyle: "medium",
            },
          ],
        },
        {
          name: "labels",
          xtype: "labelfield",
          fieldLabel: __("Labels"),
          allowBlank: true,
          query: {
            "enable_vpn": true,
          },
        },
        {
          name: "route_target",
          xtype: "gridfield",
          fieldLabel: __("Route Target"),
          allowBlank: true,
          columns: [
            {
              text: __("RD"),
              dataIndex: "rd",
              width: 75,
              editor: "textfield",
            },
            {
              text: __("Object"),
              dataIndex: "managed_object",
              width: 150,
              renderer: NOC.render.Lookup("managed_object"),
              editor: "sa.managedobject.LookupField",
            },
            {
              text: __("Operation"),
              dataIndex: "op",
              width: 75,
              editor: {
                xtype: "combobox",
                store: [
                  ["both", "both"],
                  ["import", "import"],
                  ["export", "export"],
                ],
              },
            },
            {
              text: __("Target"),
              dataIndex: "target",
              flex: 1,
              editor: "textfield",
            },
          ],
        },
      ],
    });
    me.callParent();
  },
});
