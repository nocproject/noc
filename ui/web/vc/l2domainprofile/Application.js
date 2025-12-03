//---------------------------------------------------------------------
// vc.l2domainprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.l2domainprofile.Application");

Ext.define("NOC.vc.l2domainprofile.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.label.LabelField",
    "NOC.vc.l2domainprofile.Model",
    "NOC.wf.workflow.LookupField",
    "NOC.main.style.LookupField",
    "NOC.inv.resourcepool.LookupField",
    "NOC.vc.vlantemplate.LookupField",
    "NOC.vc.vlanfilter.LookupField",
    "NOC.main.remotesystem.LookupField",
  ],
  model: "NOC.vc.l2domainprofile.Model",
  search: true,
  helpId: "vlan-profile",
  rowClassField: "row_class",

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
          text: __("Workflow"),
          dataIndex: "workflow",
          width: 100,
          renderer: NOC.render.Lookup("workflow"),
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
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "workflow",
          xtype: "wf.workflow.LookupField",
          fieldLabel: __("Workflow"),
          allowBlank: false,
        },
        {
          name: "style",
          xtype: "main.style.LookupField",
          fieldLabel: __("Style"),
          allowBlank: true,
        },
        {
          name: "vlan_discovery_policy",
          xtype: "combobox",
          fieldLabel: __("VLAN Discovery Policy"),
          allowBlank: false,
          uiStyle: "medium",
          value: "E",
          store: [
            ["D", "Disable"],
            ["E", "Enable"],
            ["S", "Status Only"],
          ],
        },
        {
          name: "vlan_discovery_filter",
          xtype: "vc.vlanfilter.LookupField",
          fieldLabel: __("VLAN Discovery Filter"),
          allowBlank: true,
        },
        {
          name: "vlan_template",
          xtype: "vc.vlantemplate.LookupField",
          fieldLabel: __("VLAN Template"),
          allowBlank: true,
        },
        {
          name: "provisioning_policy",
          xtype: "combobox",
          fieldLabel: __("VLAN Provisioning Policy"),
          allowBlank: false,
          uiStyle: "medium",
          value: "N",
          store: [
            ["D", "Disable"],
            ["E", "Enable"],
            ["A", "Add Only"],
          ],
        },
        {
          name: "pools",
          xtype: "gridfield",
          fieldLabel: __("VLAN Pools"),
          columns: [
            {
              text: __("Pool"),
              dataIndex: "pool",
              width: 200,
              editor: {
                xtype: "inv.resourcepool.LookupField",
              },
              renderer: NOC.render.Lookup("pool"),
            },
            {
              dataIndex: "description",
              text: __("Description"),
              editor: "textfield",
              width: 150,
            },
            {
              text: __("VLAN Filter"),
              dataIndex: "vlan_filter",
              width: 200,
              editor: {
                xtype: "vc.vlanfilter.LookupField",
              },
              renderer: NOC.render.Lookup("vlan_filter"),
            },
          ],
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Integration"),
          defaults: {
            padding: 4,
            labelAlign: "top",
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
            "enable_l2domainprofile": true,
          },
        },
      ],
    });
    me.callParent();
  },
});
