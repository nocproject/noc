//---------------------------------------------------------------------
// sa.service application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.service.Application");

Ext.define("NOC.sa.service.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.StateField",
    "NOC.core.InlineGrid",
    "NOC.core.label.LabelField",
    "NOC.core.combotree.ComboTree",
    "NOC.core.plugins.DynamicModalEditing",
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
    "NOC.sa.service.InstancesPanel",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.sa.service.Model",
  search: true,
  helpId: "reference-service",

  initComponent: function(){
    this.instancesPanel = Ext.create("NOC.sa.service.InstancesPanel");
    this.subscriptionPanel = Ext.create("NOC.core.SubscriptionPanel");
    this.ITEM_INSTANCES = this.registerItem(this.instancesPanel);
    this.ITEM_SUBSCRIPTION = this.registerItem(this.subscriptionPanel);
    Ext.apply(this, {
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
          text: "<i class='fa fa-bell'></i>",
          tooltip: __("Subscription"),
          dataIndex: "allow_subscribe",
          renderer: NOC.render.Subscribe,
        },
        {
          text: __("Instances"),
          dataIndex: "instance_count",
          renderer: function(value, metaData){
            metaData.tdStyle = "text-decoration-line: underline;cursor: pointer;";
            return value;
          },
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
          name: "name_template",
          xtype: "textfield",
          fieldLabel: __("Name Template"),
          allowBlank: true,
          uiStyle: "large",
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
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
          xtype: "fieldset",
          layout: "hbox",
          title: __("Referenced"),
          defaults: {
            padding: 4,
            labelAlign: "top",
          },
          items: [
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
          ],
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Agreement"),
          defaults: {
            padding: 4,
            labelAlign: "top",
          },
          items: [
            {
              name: "agreement_id",
              xtype: "textfield",
              fieldLabel: __("Agreement ID"),
              allowBlank: true,
              uiStyle: "medium",
            },
            {
              name: "account_id",
              xtype: "textfield",
              fieldLabel: __("Account ID"),
              allowBlank: true,
              uiStyle: "medium",
            },
            {
              name: "address",
              xtype: "textfield",
              fieldLabel: __("Address"),
              allowBlank: true,
              uiStyle: "large",
            },
          ],
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
          minWidth: this.formMinWidth,
          maxWidth: this.formMaxWidth,
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
          title: __("Oper Status Transfer"),
          defaults: {
            padding: 4,
            labelAlign: "top",
          },
          items: [
            {
              name: "status_transfer_policy",
              xtype: "combobox",
              fieldLabel: __("Status Transfer Policy"),
              tooltip: __("Transfer Oper Statuses to Adjacent Services <br/>" +
                  "D - Disable Status Transfer<br/>" +
                  "T - Transfer to All Adjacent<br/>" +
                  "R - Transfer By Rule<br/>" +
                  "P - From Profile"),
              store: [
                ["D", __("Disable")],
                ["P", __("By Profile")],
                ["T", __("Transparent")],
                ["R", __("By Rule")],
              ],
              allowBlank: true,
              value: "P",
              uiStyle: "medium",
              listeners: {
                render: this.addTooltip,
              },
            },
            {
              name: "status_dependencies",
              fieldLabel: __("Service Status Dependencies"),
              xtype: "gridfield",
              allowBlank: true,
              columns: [
                {
                  text: __("Service"),
                  dataIndex: "service",
                  width: 200,
                  editor: "sa.service.LookupField",
                  allowBlank: true,
                  renderer: NOC.render.Lookup("service"),
                },
                {
                  text: __("Type"),
                  dataIndex: "type",
                  width: 100,
                  editor: {
                    xtype: "combobox",
                    store: [
                      ["S", "Service (Using)"],
                      ["G", "Group"],
                      ["P", "Parent"],
                      ["C", "Children"],
                    ],
                  },
                  renderer: NOC.render.Choices({
                    "S": "Service (Using)",
                    "G": "Group",
                    "P": "Parent",
                    "C": "Children",
                  }),
                },
                {
                  text: __("Min. Status"),
                  dataIndex: "min_status",
                  width: 100,
                  editor: {
                    xtype: "combobox",
                    store: [
                      [0, "UNKNOWN"],
                      [1, "UP"],
                      [2, "SLIGHTLY_DEGRADED"],
                      [3, "DEGRADED"],
                      [4, "DOWN"],
                    ],
                  },
                  renderer: NOC.render.Choices({
                    0: "UNKNOWN",
                    1: "UP",
                    2: "SLIGHTLY_DEGRADED",
                    3: "DEGRADED",
                    4: "DOWN",
                  }),
                },
                {
                  text: __("Max. Status"),
                  dataIndex: "max_status",
                  width: 100,
                  editor: {
                    xtype: "combobox",
                    store: [
                      [0, "UNKNOWN"],
                      [1, "UP"],
                      [2, "SLIGHTLY_DEGRADED"],
                      [3, "DEGRADED"],
                      [4, "DOWN"],
                    ],
                  },
                  renderer: NOC.render.Choices({
                    0: "UNKNOWN",
                    1: "UP",
                    2: "SLIGHTLY_DEGRADED",
                    3: "DEGRADED",
                    4: "DOWN",
                  }),
                },
                {
                  text: __("Set Status"),
                  dataIndex: "set_status",
                  width: 100,
                  editor: {
                    xtype: "combobox",
                    store: [
                      [0, "UNKNOWN"],
                      [1, "UP"],
                      [2, "SLIGHTLY_DEGRADED"],
                      [3, "DEGRADED"],
                      [4, "DOWN"],
                    ],
                  },
                  renderer: NOC.render.Choices({
                    0: "UNKNOWN",
                    1: "UP",
                    2: "SLIGHTLY_DEGRADED",
                    3: "DEGRADED",
                    4: "DOWN",
                  }),
                },
                {
                  text: __("Ignored"),
                  dataIndex: "ignored",
                  width: 50,
                  renderer: NOC.render.Bool,
                  editor: "checkbox",
                },
                {
                  text: __("Weight"),
                  dataIndex: "weight",
                  editor: {
                    xtype: "numberfield",
                  },
                },
              ],
            },
          ],
        },
        {
          xtype: "fieldset",
          title: __("Calculate Oper Status"),
          defaults: {
            padding: 4,
            labelAlign: "top",
          },
          items: [
            {
              name: "calculate_status_function",
              xtype: "combobox",
              fieldLabel: __("Calculate Oper Status Policy"),
              tooltip: __("Calculate Oper Status <br/>" +
                  "D - Disable Status Transfer<br/>" +
                  "R - Transfer By Rule<br/>" +
                  "P - From Profile"),
              store: [
                ["D", __("Disable")],
                ["P", __("By Profile")],
                ["MX", __("By Max Status")],
                ["MN", __("By Min Status")],
                ["R", __("By Rule")],
              ],
              allowBlank: true,
              value: "P",
              uiStyle: "medium",
              listeners: {
                render: this.addTooltip,
              },
            },
            {
              name: "calculate_status_rules",
              fieldLabel: __("Calculate Status Rules"),
              xtype: "gridfield",
              allowBlank: true,
              columns: [
                {
                  text: __("Function"),
                  dataIndex: "weight_function",
                  width: 100,
                  editor: {
                    xtype: "combobox",
                    store: [
                      ["C", "Count"],
                      ["CP", "By Percent"],
                      ["MIN", "Minimal"],
                      ["MAX", "Maximum"],
                    ],
                  },
                  renderer: NOC.render.Choices({
                    "C": "C",
                    "CP": "CP",
                    "MIN": "MIN",
                    "MAX": "MAX",
                  }),
                },
                {
                  text: __("Op"),
                  dataIndex: "op",
                  width: 100,
                  editor: {
                    xtype: "combobox",
                    store: [
                      ["<=", "<="],
                      ["=", "="],
                      [">=", ">="],
                    ],
                  },
                  renderer: NOC.render.Choices({
                    "<=": "<=",
                    "=": "=",
                    ">=": ">=",
                  }),
                },
                {
                  text: __("Weight"),
                  dataIndex: "weight",
                  editor: {
                    xtype: "numberfield",
                  },
                },
                {
                  text: __("Min. Status"),
                  dataIndex: "min_status",
                  width: 100,
                  editor: {
                    xtype: "combobox",
                    store: [
                      [0, "UNKNOWN"],
                      [1, "UP"],
                      [2, "SLIGHTLY_DEGRADED"],
                      [3, "DEGRADED"],
                      [4, "DOWN"],
                    ],
                  },
                  renderer: NOC.render.Choices({
                    0: "UNKNOWN",
                    1: "UP",
                    2: "SLIGHTLY_DEGRADED",
                    3: "DEGRADED",
                    4: "DOWN",
                  }),
                },
                {
                  text: __("Max. Status"),
                  dataIndex: "max_status",
                  width: 100,
                  editor: {
                    xtype: "combobox",
                    store: [
                      [0, "UNKNOWN"],
                      [1, "UP"],
                      [2, "SLIGHTLY_DEGRADED"],
                      [3, "DEGRADED"],
                      [4, "DOWN"],
                    ],
                  },
                  renderer: NOC.render.Choices({
                    0: "UNKNOWN",
                    1: "UP",
                    2: "SLIGHTLY_DEGRADED",
                    3: "DEGRADED",
                    4: "DOWN",
                  }),
                },
                {
                  text: __("To Status"),
                  dataIndex: "set_status",
                  width: 100,
                  editor: {
                    xtype: "combobox",
                    store: [
                      [0, "UNKNOWN"],
                      [1, "UP"],
                      [2, "SLIGHTLY_DEGRADED"],
                      [3, "DEGRADED"],
                      [4, "DOWN"],
                    ],
                  },
                  renderer: NOC.render.Choices({
                    0: "UNKNOWN",
                    1: "UP",
                    2: "SLIGHTLY_DEGRADED",
                    3: "DEGRADED",
                    4: "DOWN",
                  }),
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
              editor: "textfield",
            },
            {
              text: __("Port"),
              dataIndex: "port_range",
              width: 50,
              editor: "textfield",
            },
          ],
        },
      ],
      inlines: [
        {
          xtype: "inlinegrid",
          title: __("Capabilities"),
          collapsible: true,
          collapsed: false,
          itemId: "sa-service-caps-inline",
          model: "NOC.sa.service.CapabilitiesModel",
          readOnly: true,
          bbar: {},
          plugins: [
            {
              ptype: "dynamicmodalediting",
              listeners: {
                canceledit: "onCancelEdit",
              },
            },
          ],
          columns: [
            {
              text: __("Capability"),
              dataIndex: "capability",
              width: 200,
            },
            {
              text: __("Value"),
              dataIndex: "value",
              useModalEditor: true,
              urlPrefix: "/sa/service",
            },
            {
              text: __("Scope"),
              dataIndex: "scope",
              width: 80,
            },
            {
              text: __("Source"),
              dataIndex: "source",
              width: 70,
            },
            {
              text: __("Description"),
              dataIndex: "description",
              flex: 1,
            },
          ],
        },
      ],
      formToolbar: [
        {
          text: __("Instances"),
          scope: this,
          handler: this.onInstances,
        },
      ],
    });
    this.callParent();
    this.getRegisteredItem(this.ITEM_GRID).addListener("beforecellclick", this.onCellClick, this); 
  },
  //
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
      title: __("By Service Group"),
      name: "effective_service_groups",
      ftype: "tree",
      lookup: "inv.resourcegroup",
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
  //
  levelFilter: {
    icon: NOC.glyph.level_down,
    color: NOC.colors.level_down,
    filter: "parent",
    tooltip: __("Parent Filter"),
  },
  //
  onPreview: function(record){
    window.open(
      "/api/card/view/service/"
            + record.get("id")
            + "/",
    )
  },
  //
  onInstances: function(){
    this.getRegisteredItem(this.ITEM_INSTANCES).load(this.currentRecord, "ITEM_FORM");
    this.showItem(this.ITEM_INSTANCES);
  },
  onCellClick: function(self, td, cellIndex, record, tr, rowIndex, e){
    var cellName = e.position.column.dataIndex;
    if(["instance_count", "allow_subscribe"].includes(cellName)){
      if(cellName === "allow_subscribe"){
        var subscriptionPanel = this.getRegisteredItem(this.ITEM_SUBSCRIPTION),
          subscriptionUrl = `sa.service/${record.id}/${subscriptionPanel.urlSuffix}/`;
        Ext.History.setHash(subscriptionUrl);
        subscriptionPanel.load(this.appId, record.get("id"), "ITEM_GRID");
        this.showItem(this.ITEM_SUBSCRIPTION);
        return false;
      }
      if(cellName === "instance_count"){
        var instancesPanel = this.getRegisteredItem(this.ITEM_INSTANCES),
          instancesUrl = `sa.service/${record.id}/${instancesPanel.urlSuffix}/`;
        Ext.History.setHash(instancesUrl);
        instancesPanel.load(this.appId, record.get("id"), "ITEM_GRID");
        this.showItem(this.ITEM_INSTANCES);
        return false;
      }
    }
    return true;
  },
});
