//---------------------------------------------------------------------
// sa.capsprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.capsprofile.Application");

Ext.define("NOC.sa.capsprofile.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.sa.capsprofile.Model",
    "NOC.inv.capability.LookupField",
    "NOC.main.label.LookupField",
    "NOC.core.label.LabelField",
  ],
  model: "NOC.sa.capsprofile.Model",
  search: true,
  viewModel: {
    data: {
      "enableSNMP": false,
      "enableL2": false,
      "enableL3": false,
    },
  },

  initComponent: function(){
    var me = this,
      policyStore = [
        ["E", __("Enable")],
        ["T", __("Enable for Topology")],
        ["D", __("Disable")],
      ];
    Ext.apply(me, {
      columns: [
        {
          text: "Name",
          dataIndex: "name",
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
          xtype: "fieldset",
          title: __("SNMP"),
          items: [
            {
              name: "enable_snmp",
              xtype: "checkbox",
              boxLabel: __("Enable SNMP"),
              reference: "enableSNMP",
            },
            {
              name: "enable_snmp_v1",
              xtype: "checkbox",
              boxLabel: __("SNMP v1"),
              bind: {
                disabled: "{!enableSNMP.checked}",
              },
            },
            {
              name: "enable_snmp_v2c",
              xtype: "checkbox",
              boxLabel: __("SNMP v2c"),
              bind: {
                disabled: "{!enableSNMP.checked}",
              },
            },
          ],
        },
        {
          xtype: "fieldset",
          title: __("L2"),
          items: [
            {
              name: "enable_l2",
              xtype: "checkbox",
              boxLabel: __("Enable L2"),
              reference: "enableL2",
            },
            {
              name: "bfd_policy",
              xtype: "combobox",
              fieldLabel: __("BFD"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL2.checked}",
              },
            },
            {
              name: "fdp_policy",
              xtype: "combobox",
              fieldLabel: __("FDP"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL2.checked}",
              },
            },
            {
              name: "huawei_ndp_policy",
              xtype: "combobox",
              fieldLabel: __("Huawei NDP"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL2.checked}",
              },
            },
            {
              name: "lacp_policy",
              xtype: "combobox",
              fieldLabel: __("LACP"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL2.checked}",
              },
            },
            {
              name: "lldp_policy",
              xtype: "combobox",
              fieldLabel: __("LLDP"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL2.checked}",
              },
            },
            {
              name: "oam_policy",
              xtype: "combobox",
              fieldLabel: __("OAM"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL2.checked}",
              },
            },
            {
              name: "rep_policy",
              xtype: "combobox",
              fieldLabel: __("REP"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL2.checked}",
              },
            },
            {
              name: "stp_policy",
              xtype: "combobox",
              fieldLabel: __("STP"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL2.checked}",
              },
            },
            {
              name: "udld_policy",
              xtype: "combobox",
              fieldLabel: __("UDLD"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL2.checked}",
              },
            },
          ],
        },
        {
          xtype: "fieldset",
          title: __("L3"),
          items: [
            {
              name: "enable_l3",
              xtype: "checkbox",
              boxLabel: __("Enable L3"),
              reference: "enableL3",
            },
            {
              name: "hsrp_policy",
              xtype: "combobox",
              fieldLabel: __("HSRP"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL3.checked}",
              },
            },
            {
              name: "vrrp_policy",
              xtype: "combobox",
              fieldLabel: __("VRRP"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL3.checked}",
              },
            },
            {
              name: "vrrpv3_policy",
              xtype: "combobox",
              fieldLabel: __("VRRP v3"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL3.checked}",
              },
            },
            {
              name: "bgp_policy",
              xtype: "combobox",
              fieldLabel: __("BGP"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL3.checked}",
              },
            },
            {
              name: "ospf_policy",
              xtype: "combobox",
              fieldLabel: __("OSPF"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL3.checked}",
              },
            },
            {
              name: "ospfv3_policy",
              xtype: "combobox",
              fieldLabel: __("OSPF v3"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL3.checked}",
              },
            },
            {
              name: "isis_policy",
              xtype: "combobox",
              fieldLabel: __("ISIS"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL3.checked}",
              },
            },
            {
              name: "ldp_policy",
              xtype: "combobox",
              fieldLabel: __("LDP"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL3.checked}",
              },
            },
            {
              name: "rsvp_policy",
              xtype: "combobox",
              fieldLabel: __("RSVP"),
              store: policyStore,
              uiStyle: "medium",
              bind: {
                disabled: "{!enableL3.checked}",
              },
            },
          ],
        },
        {
          name: "caps",
          xtype: "gridfield",
          fieldLabel: __("Capabilities"),
          allowBlank: true,
          columns: [
            {
              text: __("Name"),
              dataIndex: "capability",
              renderer: NOC.render.Lookup("capability"),
              width: 250,
              editor: "inv.capability.LookupField",
            },
            {
              text: __("Default Value"),
              dataIndex: "default_value",
              width: 150,
              editor: "textfield",
            },
            {
              text: __("Allow Manual"),
              dataIndex: "allow_manual",
              width: 150,
              editor: "checkbox",
              renderer: NOC.render.Bool,
            },
            {
              text: __("Set Label"),
              dataIndex: "set_label",
              width: 200,
              editor: {
                xtype: "main.label.LookupField",
                // filterProtected: false,
                query: {
                  "set_wildcard": true,
                },
              },
              renderer: NOC.render.Lookup("set_label"),
            },
          ],
        },
      ],
    });
    me.callParent();
  },
});
