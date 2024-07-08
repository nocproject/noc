//---------------------------------------------------------------------
// sa.service application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.service.Application");

Ext.define("NOC.sa.service.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.StateField",
    "NOC.sa.service.Model",
    "NOC.sa.service.LookupField",
    "NOC.sa.service.TreeCombo",
    "NOC.sa.serviceprofile.LookupField",
    "NOC.crm.subscriber.LookupField",
    "NOC.crm.supplier.LookupField",
    "NOC.main.remotesystem.LookupField",
    "NOC.sa.managedobject.LookupField",
    "NOC.inv.capability.LookupField",
    "NOC.inv.resourcegroup.LookupField",
    "NOC.core.label.LabelField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.sa.service.Model",
  search: true,
  helpId: "reference-service",

  initComponent: function(){
    var me = this;

    Ext.apply(me, {
      columns: [
        {
          text: __("S"),
          dataIndex: "oper_status",
          sortable: false,
          width: 30,
          renderer: function(value, metaData, record){
            var color;

            metaData.tdAttr = "data-qtip='<table style=\"font-size: 11px;\">" +
                            "<tr><td style=\"padding-right: 10px;\"><div class=\"noc-object-oper-state\" style=\"background: grey;\"></div></td><td>" + __("Unknown") + "</td></tr>" +
                            "<tr><td><div class=\"noc-object-oper-state\" style=\"background: green;\"></div></td><td>" + __("UP") + "</td></tr>" +
                            "<tr><td><div class=\"noc-object-oper-state\" style=\"background: yellow;\"></div></td><td>" + __("SLIGHTLY_DEGRADED") + "</td></tr>" +
                            "<tr><td><div class=\"noc-object-oper-state\" style=\"background: orange;\"></div></td><td>" + __("DEGRADED") + "</td></tr>" +
                            "<tr><td><div class=\"noc-object-oper-state\" style=\"background: red;\"></div></td><td>" + __("DOWN") + "</td></tr>" +
                            "<tr><td><div class=\"noc-object-oper-state\" style=\"background: linear-gradient(to right, green 50%, brown 50%);\"></div></td><td>" + __("In maintenance") + "</td></tr>" +
                "</table>'";
            switch(value){
              case "0":
                color = "grey";
                if(record.get("in_maintenance")){
                  color = "linear-gradient(to right, grey 50%, brown 50%)";
                }
                break;
              case "1":
                color = "green";
                if(record.get("in_maintenance")){
                  color = "linear-gradient(to right, green 50%, brown 50%)";
                }
                break;
              case "2":
                color = "yellow";
                if(record.get("in_maintenance")){
                  color = "linear-gradient(to right, yellow 50%, brown 50%)";
                }
                break;
              case "3":
                color = "orange";
                if(record.get("in_maintenance")){
                  color = "linear-gradient(to right, orange 50%, brown 50%)";
                }
                break;
              case "4":
                color = "red";
                if(record.get("in_maintenance")){
                  color = "linear-gradient(to right, red 50%, brown 50%)";
                }
                break;
            }

            return "<div class='noc-object-oper-state' style='background: " + color + "'></div>";
          },
        },
        {
          text: __("ID"),
          dataIndex: "id",
          width: 160,
        },
        {
          text: __("Profile"),
          dataIndex: "profile",
          width: 200,
          renderer: NOC.render.Lookup("profile"),
        },
        {
          text: __("Label"),
          dataIndex: "label",
          width: 260,
        },
        {
          text: __("Subscriber"),
          dataIndex: "subscriber",
          width: 250,
          renderer: NOC.render.Lookup("subscriber"),
        },
        {
          text: __("State"),
          dataIndex: "state",
          width: 200,
          renderer: NOC.render.Lookup("state"),
        },
        {
          text: __("Parent"),
          dataIndex: "parent",
          flex: 1,
        },
      ],

      fields: [
        {
          name: "profile",
          xtype: "sa.serviceprofile.LookupField",
          fieldLabel: __("Profile"),
          allowBlank: false,
        },
        {
          name: "state",
          xtype: "statefield",
          fieldLabel: __("State"),
          allowBlank: true,
        },
        {
          name: "labels",
          xtype: "labelfield",
          fieldLabel: __("Labels"),
          query: {
            "allow_models": ["sa.Service"],
          },
        },
        {
          name: "parent",
          xtype: "sa.service.LookupField",
          fieldLabel: __("Parent"),
          allowBlank: true,
        },
        {
          name: "subscriber",
          xtype: "crm.subscriber.LookupField",
          fieldLabel: __("Subscriber"),
          allowBlank: true,
        },
        {
          name: "supplier",
          xtype: "crm.supplier.LookupField",
          fieldLabel: __("Supplier"),
          allowBlank: true,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Agreement"),
          defaults: {
            padding: 4,
            labelAlign: "top"
          },
          items: [
            {
                name: "agreement_id",
                xtype: "textfield",
                fieldLabel: __("Agreement ID"),
                allowBlank: true,
                uiStyle: "medium"
            },
            {
                name: "account_id",
                xtype: "textfield",
                fieldLabel: __("Account ID"),
                allowBlank: true,
                uiStyle: "medium"
            },
            {
                name: "address",
                xtype: "textfield",
                fieldLabel: __("Address"),
                allowBlank: true,
                uiStyle: "large"
            }
          ]
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("CPE"),
          defaults: {
            padding: 4,
            labelAlign: "top",
          },
          items: [
            {
              name: "cpe_serial",
              xtype: "textfield",
              fieldLabel: __("Serial"),
              allowBlank: true,
              uiStyle: "medium",
            },
            {
              name: "cpe_mac",
              xtype: "textfield",
              fieldLabel: __("MAC"),
              allowBlank: true,
              uiStyle: "medium",
            },
          ],
        },
        {
          xtype: "fieldset",
          title: __("Resource Groups"),
          layout: "column",
          minWidth: me.formMinWidth,
          maxWidth: me.formMaxWidth,
          defaults: {
            columnWidth: 0.5,
            padding: 10,
          },
          collapsible: true,
          collapsed: false,
          items: [
            {
              name: "static_service_groups",
              xtype: "gridfield",
              columns: [
                {
                  dataIndex: "group",
                  text: __("Static Service Groups"),
                  width: 350,
                  renderer: NOC.render.Lookup("group"),
                  editor: {
                    xtype: "inv.resourcegroup.LookupField",
                  },
                },
              ],
            },
            {
              name: "effective_service_groups",
              xtype: "gridfield",
              columns: [
                {
                  dataIndex: "group",
                  text: __("Effective Service Groups"),
                  width: 350,
                  renderer: NOC.render.Lookup("group"),
                  editor: {
                    xtype: "inv.resourcegroup.LookupField",
                  },
                },
              ],
            },
            {
              name: "static_client_groups",
              xtype: "gridfield",
              columns: [
                {
                  dataIndex: "group",
                  text: __("Static Client Groups"),
                  width: 350,
                  renderer: NOC.render.Lookup("group"),
                  editor: {
                    xtype: "inv.resourcegroup.LookupField",
                  },
                },
              ],
            },
            {
              name: "effective_client_groups",
              xtype: "gridfield",
              columns: [
                {
                  dataIndex: "group",
                  text: __("Effective Client Groups"),
                  width: 350,
                  renderer: NOC.render.Lookup("group"),
                  editor: {
                    xtype: "inv.resourcegroup.LookupField",
                  },
                },
              ],
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
          name: "static_instances",
          xtype: "gridfield",
          fieldLabel: __("Static Instances"),
          allowBlank: true,
          columns: [
            {
              text: __("Name"),
              dataIndex: "textfield",
              width: 250,
              editor: "textfield"
            },
            {
              text: __("Port"),
              dataIndex: "port_range",
              width: 50,
              editor: "textfield"
            },
          ]
        },
        {
          name: "instances",
          xtype: "gridfield",
          fieldLabel: __("Instances"),
          allowBlank: true,
          columns: [
            {
              text: __("Name"),
              dataIndex: "textfield",
              width: 250,
              editor: "textfield"
            },
            {
              text: __("Address"),
              dataIndex: "address",
              width: 100,
              editor: "textfield"
            },
            {
              text: __("FQDN"),
              dataIndex: "fqdn",
              width: 100,
              editor: "textfield"
            },
            {
              text: __("Port"),
              dataIndex: "port",
              width: 50,
              editor: "numberfield"
            },
            {
              text: __("NRI Port"),
              dataIndex: "nri_port",
              width: 100,
              editor: "textfield"
            }
          ]
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
              text: __("Value"),
              dataIndex: "value",
              flex: 1,
              editor: "textfield",
            },
            {
              text: __("Source"),
              dataIndex: "source",
              width: 100,
              editor: "textfield",
            },
            {
              text: __("Scope"),
              dataIndex: "scope",
              width: 50,
              editor: "textfield",
            },
          ],
        }
      ],
    });
    me.callParent();
  },

  filters: [
    {
      title: __("By Service"),
      name: "parent",
      ftype: "tree",
      lookup: "sa.service",
    },
    {
      title: __("By Profile"),
      name: "profile",
      ftype: "lookup",
      lookup: "sa.serviceprofile",
    },
    {
      title: __("By Subscriber"),
      name: "subscriber",
      ftype: "lookup",
      lookup: "crm.subscriber",
    },
    {
      title: __("By Supplier"),
      name: "supplier",
      ftype: "lookup",
      lookup: "crm.supplier",
    },
    {
      title: __("By State"),
      name: "state",
      ftype: "lookup",
      lookup: "wf.state",
    },
  ],

  levelFilter: {
    icon: NOC.glyph.level_down,
    color: NOC.colors.level_down,
    filter: 'parent',
    tooltip: __('Parent Filter'),
  },

  onPreview: function(record){
    window.open(
      "/api/card/view/service/"
            + record.get("id")
            + "/",
    )
  },
});
