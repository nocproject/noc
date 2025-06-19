//---------------------------------------------------------------------
// sa.managedobjectprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobjectprofile.Application");

Ext.define("NOC.sa.managedobjectprofile.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.sa.managedobjectprofile.Model",
    "NOC.sa.managedobjectprofile.LookupField",
    "NOC.sa.authprofile.LookupField",
    "NOC.sa.capsprofile.LookupField",
    "NOC.peer.peerprofile.LookupField",
    "NOC.main.style.LookupField",
    "NOC.main.ref.stencil.LookupField",
    "NOC.main.ref.windowfunction.LookupField",
    "NOC.pm.metrictype.LookupField",
    "NOC.main.remotesystem.LookupField",
    "NOC.ip.prefixprofile.LookupField",
    "NOC.ip.addressprofile.LookupField",
    "NOC.vc.vpnprofile.LookupField",
    "NOC.vc.vlanfilter.LookupField",
    "NOC.main.template.LookupField",
    "NOC.main.extstorage.LookupField",
    "NOC.main.handler.LookupField",
    "NOC.inv.ifdescpatterns.LookupField",
    "NOC.cm.objectvalidationpolicy.LookupField",
    "NOC.main.glyph.LookupField",
    "NOC.main.ref.soposition.LookupField",
    "NOC.main.ref.soform.LookupField",
    "NOC.core.label.LabelField",
    "NOC.core.ListFormField",
    "Ext.ux.form.MultiIntervalField",
    "Ext.ux.form.GridField",
    "NOC.wf.workflow.LookupField",
  ],
  model: "NOC.sa.managedobjectprofile.Model",
  search: true,
  helpId: "reference-managed-object-profile",
  rowClassField: "row_class",
  validationModelId: "sa.ManagedObjectProfile",
  viewModel: {
    data: {
      enableBoxDiscoveryVersion: false,
      enableBoxDiscoveryConfig: false,
      enableBoxDiscoveryCaps: false,
      enableBoxDiscoveryInterface: false,
      enableBoxDiscoveryBGPPeer: false,
      enableBoxDiscoveryVLAN: false,
      enableBoxDiscoveryVPNInterface: false,
      enableBoxDiscoveryVPNMPLS: false,
      enableBoxDiscoveryVPNConfDB: false,
      enableBoxDiscoveryPrefixInterface: false,
      enableBoxDiscoveryPrefixNeighbor: false,
      enableBoxDiscoveryPrefixConfDB: false,
      enableBoxDiscoveryAddressInterface: false,
      enableBoxDiscoveryAddressManagement: false,
      enableBoxDiscoveryAddressDHCP: false,
      enableBoxDiscoveryAddressNeighbor: false,
      enableBoxDiscoveryAddressConfDB: false,
      enableBoxDiscoveryHK: false,
      enableBoxDiscoveryNRIPortmap: false,
      enableBoxDiscoveryIfDesc: false,
      enableFMRCADownlinkMerge: false,
    },
    formulas: {
      disableConfigMirrorPolicy: {
        bind: {
          bindTo: "{mirrorPolicy.selection}",
          deep: true,
        },
        get: function(record){
          return record ? this.data.enableBoxDiscoveryConfig.checked
                        && record.get("id") === "D" : true;
        },
      },
      disableConfigPolicy: {
        bind: {
          bindTo: "{configPolicy.selection}",
          deep: true,
        },
        get: function(record){
          return record ? this.data.enableBoxDiscoveryConfig.checked
                        && (record.get("id") === "s") : true;
        },
      },
      disableBeefPolicy: {
        bind: {
          bindTo: "{beefPolicy.selection}",
          deep: true,
        },
        get: function(record){
          return record ? record.get("id") === "D" : true;
        },
      },
    },
  },

  initComponent: function(){
    var me = this;

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
        },
        {
          text: __("Level"),
          dataIndex: "level",
          width: 60,
          align: "right",
        },
        {
          text: __("Ping"),
          dataIndex: "enable_ping",
          width: 100,
          renderer: function(value, meta, record){
            var v = NOC.render.Bool(value);
            if(value){
              v += " " + NOC.render.Duration(record.get("ping_interval"));
              if(record.get("report_ping_rtt")){
                v += "+RTT"
              }
            }
            return v
          },
          align: "center",
        },
        {
          text: __("Box discovery"),
          dataIndex: "enable_box_discovery",
          width: 100,
          renderer: function(value, meta, record){
            var v = NOC.render.Bool(value);
            if(value){
              v += " " + NOC.render.Duration(record.get("box_discovery_interval"));
            }
            return v
          },
          align: "center",
        },
        {
          text: __("Failed interval"),
          dataIndex: "box_discovery_failed_interval",
          width: 100,
          renderer: NOC.render.Duration,
          align: "center",
        },
        {
          text: __("Periodic discovery"),
          dataIndex: "enable_periodic_discovery",
          width: 100,
          renderer: function(value, meta, record){
            var v = NOC.render.Bool(value);
            if(value){
              v += " " + NOC.render.Duration(record.get("periodic_discovery_interval"));
            }
            return v
          },
          align: "center",
        },
        {
          text: __("Objects"),
          dataIndex: "mo_count",
          width: 60,
          align: "right",
          sortable: false,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          width: 300,
          sortable: false,
          renderer: function(value, meta){
            meta.tdAttr = 'data-qtip="' + value + '"';
            return value
          },
        },
      ],
      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          autoFocus: true,
          allowBlank: false,
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
                  name: "description",
                  xtype: "textarea",
                  fieldLabel: __("Description"),
                  allowBlank: true,
                  uiStyle: "extra",
                },
                {
                  name: "level",
                  xtype: "numberfield",
                  fieldLabel: __("Level"),
                  allowBlank: false,
                  uiStyle: "small",
                },
                {
                  name: "labels",
                  xtype: "labelfield",
                  fieldLabel: __("Labels"),
                  allowBlank: true,
                  uiStyle: "extra",
                  query: {
                    "allow_models": ["sa.ManagedObjectProfile"],
                  },
                },
                {
                  name: "workflow",
                  xtype: "wf.workflow.LookupField",
                  fieldLabel: __("WorkFlow"),
                  uiStyle: "medium",
                  allowBlank: true,
                },
                {
                  xtype: "fieldset",
                  title: __("Display Settings"),
                  layout: "vbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      xtype: "container",
                      layout: "hbox",
                      defaults: {
                        padding: "0 8 0 0",
                      },
                      items: [
                        {
                          name: "style",
                          xtype: "main.style.LookupField",
                          fieldLabel: __("Style"),
                          allowBlank: true,
                        },
                        {
                          name: "shape",
                          xtype: "main.ref.stencil.LookupField",
                          fieldLabel: __("Shape"),
                          allowBlank: true,
                        },
                        {
                          name: "shape_title_template",
                          xtype: "textfield",
                          fieldLabel: __("Shape Name template"),
                          allowBlank: true,
                          uiStyle: "large",
                        },
                      ],
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Badge"),
                  layout: "vbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      xtype: "container",
                      layout: "hbox",
                      defaults: {
                        padding: "0 8 0 0",
                      },
                      items: [
                        {
                          name: "shape_overlay_glyph",
                          xtype: "main.glyph.LookupField",
                          fieldLabel: __("Glyph"),
                          allowBlank: true,
                        },
                        {
                          name: "shape_overlay_position",
                          xtype: "main.ref.soposition.LookupField",
                          fieldLabel: __("Position"),
                          allowBlank: true,
                        },
                        {
                          name: "shape_overlay_form",
                          xtype: "main.ref.soform.LookupField",
                          fieldLabel: __("Form"),
                          allowBlank: true,
                        },
                      ],
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Integration"),
                  tooltip: __("Field on this use in ETL process (sync on external system). <br/>" +
                                        "Do not Edit field directly!"),
                  layout: "vbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      xtype: "container",
                      layout: "hbox",
                      defaults: {
                        padding: "0 8 0 0",
                      },
                      items: [
                        {
                          name: "remote_system",
                          xtype: "main.remotesystem.LookupField",
                          labelWidth: 150,
                          fieldLabel: __("Remote System"),
                          allowBlank: true,
                        },
                        {
                          name: "remote_id",
                          xtype: "textfield",
                          labelWidth: 150,
                          fieldLabel: __("Remote ID"),
                          allowBlank: true,
                          uiStyle: "medium",
                        },
                        {
                          name: "bi_id",
                          xtype: "displayfield",
                          labelWidth: 150,
                          fieldLabel: __("BI ID"),
                          allowBlank: true,
                          uiStyle: "medium",
                        },
                      ],

                    },
                  ],
                  listeners: {
                    render: me.addTooltip,
                  },
                },
                {
                  xtype: "fieldset",
                  title: __("Address Resolution Policy"),
                  layout: "hbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "address_resolution_policy",
                      xtype: "combobox",
                      fieldLabel: __("Address Resolution Policy"),
                      store: [
                        ["D", __("Disabled")],
                        ["O", __("Once")],
                        ["E", __("Enabled")],
                      ],
                      allowBlank: false,
                      labelWidth: 200,
                      value: "D",
                      uiStyle: "large",
                    },
                    {
                      name: "resolver_handler",
                      xtype: "main.handler.LookupField",
                      fieldLabel: __("Resolver Handler"),
                      allowBlank: true,
                      uiStyle: "medium",
                      query: {
                        allow_resolver: true,
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("IPAM Field"),
                  layout: "hbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "name_template",
                      xtype: "textfield",
                      fieldLabel: __("Name template"),
                      allowBlank: true,
                      uiStyle: "large",
                    },
                    {
                      name: "fqdn_suffix",
                      xtype: "textfield",
                      fieldLabel: __("FQDN Suffix"),
                      allowBlank: true,
                      uiStyle: "large",
                    },
                  ],
                },
                {
                  name: "dynamic_classification_policy",
                  xtype: "combobox",
                  fieldLabel: __("Dynamic Classification Policy"),
                  store: [
                    ["D", __("Disabled")],
                    ["R", __("By Rule")],
                  ],
                  allowBlank: false,
                  labelWidth: 200,
                  value: "R",
                  uiStyle: "medium",
                },
                {
                  name: "match_rules",
                  xtype: "listform",
                  rows: 6,
                  labelAlign: "top",
                  uiStyle: "large",
                  fieldLabel: __("Match Rules"),
                  items: [
                    {
                      name: "dynamic_order",
                      xtype: "numberfield",
                      fieldLabel: __("Dynamic Order"),
                      allowBlank: true,
                      defaultValue: 0,
                      uiStyle: "small",
                    },
                    {
                      name: "labels",
                      xtype: "labelfield",
                      fieldLabel: __("Match Labels"),
                      allowBlank: false,
                      isTree: true,
                      filterProtected: false,
                      pickerPosition: "down",
                      uiStyle: "extra",
                      query: {
                        "allow_matched": true,
                      },
                    },
                    {
                      name: "handler",
                      xtype: "main.handler.LookupField",
                      fieldLabel: __("Match Handler"),
                      allowBlank: true,
                      uiStyle: "medium",
                      query: {
                        "allow_match_rule": true,
                      },
                    },
                  ],
                },
              ],
            },
            {
              title: __("Access"),
              tooltip: __("Worked with devices settings"),
              items: [
                {
                  name: "access_preference",
                  xtype: "combobox",
                  tooltip: __("Protocol priority worked on device. <br/>" +
                                        "Warning! Device profile (SA Profile) should support worked in selected mode"),
                  fieldLabel: __("Access Preference"),
                  labelWidth: 220,
                  allowBlank: false,
                  uiStyle: "medium",
                  store: [
                    ["S", __("SNMP Only")],
                    ["C", __("CLI Only")],
                    ["SC", __("SNMP, CLI")],
                    ["CS", __("CLI, SNMP")],
                  ],
                  value: "CS",
                  listeners: {
                    render: me.addTooltip,
                  },
                },
                {
                  name: "cli_session_policy",
                  xtype: "combobox",
                  tooltip: __("Use one session worked on device. <br/>" +
                                        "If disabled - worked one script - one login. Logout after script end."),
                  fieldLabel: __("CLI Session Policy"),
                  labelWidth: 220,
                  allowBlank: true,
                  labelAlign: "left",
                  uiStyle: "medium",
                  store: [
                    ["E", __("Enable")],
                    ["D", __("Disable")],
                  ],
                  value: "E",
                  listeners: {
                    render: me.addTooltip,
                  },
                },
                {
                  name: "cli_privilege_policy",
                  xtype: "combobox",
                  tooltip: __("Do enable if login unprivileged mode on device. <br/>" +
                                        "Raise Privileges - send enable, Do not raise - work on current mode <br/>" +
                                        "(immediately after login)"),
                  fieldLabel: __("CLI Privilege Policy"),
                  labelWidth: 220,
                  allowBlank: true,
                  uiStyle: "medium",
                  store: [
                    ["D", __("Do not raise")],
                    ["E", __("Raise Privileges")],
                  ],
                  value: "E",
                  listeners: {
                    render: me.addTooltip,
                  },
                },
                {
                  name: "snmp_rate_limit",
                  xtype: "numberfield",
                  fieldLabel: __("SNMP Rate limit"),
                  labelWidth: 220,
                  tooltip: __(
                    "Limit SNMP (Query per second).",
                  ),
                  uiStyle: "small",
                  allowBlank: true,
                  minValue: 0,
                  maxValue: 99,
                  listeners: {
                    render: me.addTooltip,
                  },
                },
              ],
              listeners: {
                render: me.addTooltip,
              },
            },
            {
              title: __("Card"),
              items: [
                {
                  name: "card",
                  xtype: "textfield",
                  fieldLabel: __("Card"),
                  labelWidth: 200,
                  allowBlank: true,
                  uiStyle: "extra",
                },
                {
                  name: "card_title_template",
                  xtype: "textfield",
                  fieldLabel: __("Card Title Template"),
                  labelWidth: 200,
                  allowBlank: false,
                  uiStyle: "extra",
                },
              ],
            },
            {
              title: __("Ping Check"),
              items: [
                {
                  name: "enable_ping",
                  xtype: "checkboxfield",
                  boxLabel: __("Enable"),
                  allowBlank: false,

                },
                {
                  xtype: "fieldset",
                  title: __("Ping discovery intervals"),
                  layout: "vbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      xtype: "container",
                      layout: "hbox",
                      defaults: {
                        padding: "0 8 0 0",
                      },
                      items: [
                        {
                          name: "ping_interval",
                          xtype: "numberfield",
                          fieldLabel: __("Interval, sec"),
                          uiStyle: "small",
                          minValue: 0,
                          listeners: {
                            scope: me,
                            change: function(_item, newValue){
                              me.form.findField("ping_calculated").setValue(newValue);
                            },
                          },
                        },
                        {
                          name: "ping_calculated",
                          xtype: "displayfield",
                          renderer: NOC.render.Duration,
                        },
                        {
                          name: "ping_time_expr_policy",
                          xtype: "combobox",
                          tooltip: __("Enable or disable ping if working hour on object is set. <br/>" +
                                                        "Enable - Calc RTT, but do not raise alarm, Disable ping - do not send ICMP"),
                          fieldLabel: __("Policy Off Hours"),
                          labelWidth: 120,
                          allowBlank: true,
                          uiStyle: "medium",
                          store: [
                            ["D", __("Disable ping")],
                            ["E", __("Enable ping but don't follow status")],
                          ],
                          value: "D",
                          listeners: {
                            render: me.addTooltip,
                          },
                        },
                      ],
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Ping series settings"),
                  layout: "vbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "ping_policy",
                      xtype: "combobox",
                      labelAlign: "left",
                      labelWidth: 220,
                      fieldLabel: __("Ping Policy"),
                      allowBlank: true,
                      uiStyle: "medium",
                      store: [
                        ["f", __("First Success")],
                        ["a", __("All Success")],
                      ],
                      value: "f",
                    },
                    {
                      xtype: "container",
                      layout: "hbox",
                      defaults: {
                        padding: "0 8 0 0",
                      },
                      items: [
                        {
                          name: "ping_size",
                          xtype: "numberfield",
                          fieldLabel: __("Packet size, bytes"),
                          labelWidth: 220,
                          uiStyle: "small",
                          defaultValue: 64,
                          minValue: 64,
                        },
                      ],
                    },
                    {
                      xtype: "container",
                      layout: "hbox",
                      defaults: {
                        padding: "0 8 0 0",
                      },
                      items: [
                        {
                          name: "ping_count",
                          xtype: "numberfield",
                          fieldLabel: __("Packets count"),
                          labelWidth: 220,
                          defaultValue: 3,
                          minValue: 0,
                          uiStyle: "small",
                        },
                      ],
                    },
                    {
                      xtype: "container",
                      layout: "hbox",
                      defaults: {
                        padding: "0 8 0 0",
                      },
                      items: [
                        {
                          name: "ping_timeout_ms",
                          xtype: "numberfield",
                          fieldLabel: __("Timeout, msec"),
                          defaultValue: 1000,
                          minValue: 0,
                          labelWidth: 220,
                          uiStyle: "small",
                          listeners: {
                            scope: me,
                            change: function(_item, newValue){
                              me.form.findField("ping_tm_calculated").setValue(newValue / 1000);
                            },
                          },
                        },
                        {
                          name: "ping_tm_calculated",
                          xtype: "displayfield",
                          renderer: NOC.render.Duration,
                        },
                      ],
                    },
                  ],
                },
                {
                  name: "report_ping_rtt",
                  xtype: "checkboxfield",
                  boxLabel: __("Report ping RTT"),
                  allowBlank: false,
                },
                {
                  name: "report_ping_attempts",
                  xtype: "checkboxfield",
                  boxLabel: __("Report ping attempts"),
                  allowBlank: false,
                },
              ],
            },
            {
              title: "FM",
              items: [
                {
                  name: "event_processing_policy",
                  xtype: "combobox",
                  tooltip: __("Processed syslog/snmp trap message to Classifier service <br/>" +
                                        "E - Send message to Classifier<br/>" +
                                        "D - Do not send message to Classifier"),
                  labelWidth: 150,
                  fieldLabel: __("Event Policy"),
                  store: [
                    ["E", __("Enable")],
                    ["D", __("Disable")],
                  ],
                  value: "E",
                  allowBlank: false,
                  uiStyle: "medium",
                  listeners: {
                    render: me.addTooltip,
                  },
                },
                {
                  name: "weight",
                  xtype: "numberfield",
                  labelWidth: 150,
                  fieldLabel: __("Alarm Weight"),
                  allowBlank: false,
                  uiStyle: "small",
                },
                {
                  name: "syslog_archive_policy",
                  xtype: "combobox",
                  tooltip: __("Enable send syslog message to ClickHouse </b>syslog</b> table. <br/>" +
                                        "May be overwritten by ManageObject <b>syslog_archive_policy</b> setting. <br/>" +
                                        "E - Send syslog message to ClickHouse<br/>" +
                                        "D - Do not send syslog message to ClickHouse"),
                  labelWidth: 150,
                  fieldLabel: __("Syslog Archive Policy"),
                  store: [
                    ["E", __("Enable")],
                    ["D", __("Disable")],
                  ],
                  value: "D",
                  allowBlank: true,
                  uiStyle: "medium",
                  listeners: {
                    render: me.addTooltip,
                  },
                },
                {
                  name: "escalation_policy",
                  xtype: "combobox",
                  tooltip: __("Enable - allow to escalate alarm for ManagedObject. <br/>" +
                                        "As Depended - allow to escalate ManagedObject only as depend (not root) on alarm"),
                  labelWidth: 150,
                  fieldLabel: __("Escalation Policy"),
                  allowBlank: true,
                  uiStyle: "medium",
                  store: [
                    ["E", __("Enable")],
                    ["D", __("Disable")],
                    ["R", __("As Depended")],
                  ],
                  value: "E",
                  listeners: {
                    render: me.addTooltip,
                  },
                },
                {
                  xtype: "fieldset",
                  layout: "hbox",
                  title: __("Merge Downlinks"),
                  defaults: {
                    padding: 4,
                  },
                  items: [
                    {
                      name: "enable_rca_downlink_merge",
                      xtype: "checkbox",
                      boxLabel: __("Enable"),
                      reference: "enableFMRCADownlinkMerge",
                    },
                    {
                      name: "rca_downlink_merge_window",
                      xtype: "numberfield",
                      minValue: 0,
                      fieldLabel: __("Merge Window (sec)"),
                      labelWidth: 150,
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableFMRCADownlinkMerge.checked}",
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  layout: "hbox",
                  title: __("Abduct Detection"),
                  defaults: {
                    padding: 4,
                  },
                  items: [
                    {
                      name: "abduct_detection_window",
                      fieldLabel: __("Abduct Detection Window"),
                      labelWidth: 150,
                      xtype: "numberfield",
                      allowBlank: true,
                      uiStyle: "small",
                    },
                    {
                      name: "abduct_detection_threshold",
                      fieldLabel: __("Abduct Detection Threshold"),
                      labelWidth: 200,
                      xtype: "numberfield",
                      allowBlank: true,
                      uiStyle: "small",
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  layout: "hbox",
                  title: __("Trap Collector Storm Settings"),
                  defaults: {
                    padding: 4,
                  },
                  items: [
                    {
                      name: "trapcollector_storm_policy",
                      xtype: "combobox",
                      tooltip: __("Check Device SNMP Trap storm policy <br/>" +
                                                "check trap message count over 60s <br/>" +
                                                "B - Block receive trap from ManagedObject Address<br/>" +
                                                "R - Raise Alarm to ManagedObject and not block<br/>" +
                                                "A - Raise Alarm to ManagedObject and block trap receive<br/>" +
                                                "D - Disable Storm Check"),
                      labelWidth: 150,
                      fieldLabel: __("Storm Policy"),
                      store: [
                        ["B", __("Block")],
                        ["R", __("Raise Alarm")],
                        ["A", __("Block & Raise Alarm")],
                        ["D", __("Disable")],
                      ],
                      value: "D",
                      allowBlank: true,
                      uiStyle: "medium",
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                    {
                      name: "trapcollector_storm_threshold",
                      fieldLabel: __("Message Storm Threshold"),
                      labelWidth: 200,
                      xtype: "numberfield",
                      allowBlank: true,
                      uiStyle: "small",
                    },
                  ],
                },
              ],
            },
            {
              title: __("Box discovery"),
              items: [
                {
                  xtype: "fieldset",
                  layout: "vbox",
                  items: [
                    {
                      name: "enable_box_discovery",
                      xtype: "checkbox",
                      boxLabel: __("Enable"),
                    },
                    {
                      name: "box_discovery_running_policy",
                      xtype: "combobox",
                      fieldLabel: __("Running Policy"),
                      store: [
                        ["R", __("Require Up")],
                        ["r", __("Require Up if ping enabled")],
                        ["i", __("Always Run")],
                      ],
                      labelWidth: 250,
                      allowBlank: false,
                      uiStyle: "medium",
                      padding: "0 0 0 8px",
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Box discovery intervals"),
                  layout: "vbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      xtype: "container",
                      layout: "hbox",
                      defaults: {
                        padding: "0 8 0 4px",
                      },
                      items: [
                        {
                          name: "box_discovery_interval",
                          xtype: "numberfield",
                          fieldLabel: __("Interval, sec"),
                          labelWidth: 250,
                          allowBlank: false,
                          uiStyle: "small",
                          minValue: 0,
                          listeners: {
                            scope: me,
                            change: function(_item, newValue){
                              me.form.findField("box_discovery_interval_calculated").setValue(newValue);
                            },
                          },
                        },
                        {
                          name: "box_discovery_interval_calculated",
                          xtype: "displayfield",
                          renderer: NOC.render.Duration,
                        },
                      ],
                    },
                    {
                      xtype: "container",
                      layout: "hbox",
                      defaults: {
                        padding: "0 8 0 4px",
                      },
                      items: [
                        {
                          name: "box_discovery_failed_interval",
                          xtype: "numberfield",
                          fieldLabel: __("Failed Interval, sec"),
                          labelWidth: 250,
                          minValue: 0,
                          allowBlank: false,
                          uiStyle: "small",
                          listeners: {
                            scope: me,
                            change: function(_item, newValue){
                              me.form.findField("box_discovery_failed_interval_calculated").setValue(newValue);
                            },
                          },
                        },
                        {
                          name: "box_discovery_failed_interval_calculated",
                          xtype: "displayfield",
                          renderer: NOC.render.Duration,
                        },
                      ],
                    },
                    {
                      xtype: "container",
                      layout: "hbox",
                      defaults: {
                        padding: "0 8 0 4px",
                      },
                      items: [
                        {
                          name: "box_discovery_on_system_start",
                          xtype: "checkbox",
                          width: 243,
                          boxLabel: __("Check on system start after "),
                        },
                        {
                          name: "box_discovery_system_start_delay",
                          xtype: "numberfield",
                          labelWidth: -5,
                          minValue: 0,
                          allowBlank: false,
                          uiStyle: "small",
                        },  
                        {
                          name: "_box_discovery_system_start_delay",
                          xtype: "displayfield",
                          value: __("sec"),
                        },
                      ],
                    },
                    {
                      xtype: "container",
                      layout: "hbox",
                      defaults: {
                        padding: "0 8 0 4px",
                      },
                      items: [
                        {
                          name: "box_discovery_on_config_changed",
                          xtype: "checkbox",
                          width: 243,
                          boxLabel: __("Check on config change after "),
                        },
                        {
                          name: "box_discovery_config_changed_delay",
                          xtype: "numberfield",
                          minValue: 0,
                          labelWidth: -5,
                          allowBlank: false,
                          uiStyle: "small",
                        },
                        {
                          name: "_box_discovery_config_changed_delay",
                          xtype: "displayfield",
                          value: __("sec"),
                        },
                      ],
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Box"),
                  layout: {
                    type: "table",
                    columns: 3,
                  },
                  defaults: {
                    padding: "0 8 0 0",
                  },
                  items: [
                    {
                      name: "enable_box_discovery_profile",
                      xtype: "checkboxfield",
                      boxLabel: __("Profile"),
                      colspan: 3,
                    },
                    {
                      name: "enable_box_discovery_version",
                      xtype: "checkboxfield",
                      boxLabel: __("Version"),
                      reference: "enableBoxDiscoveryVersion",
                      colspan: 3,
                    },
                    {
                      name: "enable_box_discovery_caps",
                      xtype: "checkboxfield",
                      boxLabel: __("Caps"),
                      reference: "enableBoxDiscoveryCaps",
                    },
                    {
                      name: "caps_discovery_policy",
                      xtype: "combobox",
                      fieldLabel: __("Policy"),
                      store: [
                        ["s", __("Script")],
                        ["S", __("Script, ConfDB")],
                        ["C", __("ConfDB, Script")],
                        ["c", __("ConfDB")],
                      ],
                      allowBlank: false,
                      bind: {
                        disabled: "{!enableBoxDiscoveryCaps.checked}",
                      },
                      uiStyle: "medium",
                    },
                    {
                      name: "caps_profile",
                      xtype: "sa.capsprofile.LookupField",
                      tooltip: __("Set which CAPS will be check in Caps discovery. <br/>" +
                                                "Service Activation -> Setup -> Caps Profiles"),
                      fieldLabel: __("Caps Profile"),
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryCaps.checked}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                    {
                      name: "enable_box_discovery_interface",
                      xtype: "checkboxfield",
                      boxLabel: __("Interface"),
                      reference: "enableBoxDiscoveryInterface",
                    },
                    {
                      name: "interface_discovery_policy",
                      xtype: "combobox",
                      fieldLabel: __("Policy"),
                      store: [
                        ["s", __("Script")],
                        ["S", __("Script, ConfDB")],
                        ["C", __("ConfDB, Script")],
                        ["c", __("ConfDB")],
                      ],
                      allowBlank: false,
                      bind: {
                        disabled: "{!enableBoxDiscoveryInterface.checked}",
                      },
                      uiStyle: "medium",
                    },
                    {
                      name: "enable_interface_autocreation",
                      xtype: "checkbox",
                      boxLabel: __("Enable Autocreation"),
                      bind: {
                        disabled: "{enableBoxDiscoveryInterface.checked}",
                      },
                    },
                    {
                      name: "enable_box_discovery_id",
                      xtype: "checkboxfield",
                      boxLabel: __("ID"),
                      colspan: 3,
                    },
                    {
                      name: "enable_box_discovery_config",
                      xtype: "checkboxfield",
                      boxLabel: __("Config"),
                      reference: "enableBoxDiscoveryConfig",
                      colspan: 3,
                    },
                    {
                      name: "enable_box_discovery_asset",
                      xtype: "checkboxfield",
                      boxLabel: __("Asset"),
                      colspan: 3,
                    },
                    {
                      name: "enable_box_discovery_cpe",
                      xtype: "checkboxfield",
                      boxLabel: __("CPE"),
                      colspan: 3,
                    },
                    {
                      name: "enable_box_discovery_bgppeer",
                      xtype: "checkboxfield",
                      boxLabel: __("BGP Peer"),
                      reference: "enableBoxDiscoveryBGPPeer",
                    },
                    {
                      name: "bgpeer_discovery_policy",
                      xtype: "combobox",
                      fieldLabel: __("Policy"),
                      store: [
                        ["c", __("ConfDB")],
                      ],
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryBGPPeer.checked}",
                      },
                      uiStyle: "medium",
                    },
                    {
                      name: "bgppeer_profile",
                      xtype: "peer.peerprofile.LookupField",
                      tooltip: __("Set which Peer Profile will be set when Created. <br/>" +
                                                "Peer -> Setup -> Peer Profiles"),
                      fieldLabel: __("BGP Peer Profile"),
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryBGPPeer.checked}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Topology"),
                  layout: "vbox",
                  items: [
                    {
                      xtype: "container",
                      layout: {
                        type: "column",
                        // wrap: true,
                      },
                      defaults: {
                        padding: "0 8 0 0",
                      },
                      items: [
                        {
                          name: "enable_box_discovery_nri",
                          xtype: "checkboxfield",
                          boxLabel: __("NRI"),
                          bind: {
                            disabled: "{!enableBoxDiscoveryNRIPortmap.checked}",
                          },
                        },
                        {
                          name: "enable_box_discovery_bfd",
                          xtype: "checkboxfield",
                          boxLabel: __("BFD"),
                        },
                        {
                          name: "enable_box_discovery_cdp",
                          xtype: "checkboxfield",
                          boxLabel: __("CDP"),
                        },
                        {
                          name: "enable_box_discovery_huawei_ndp",
                          xtype: "checkboxfield",
                          boxLabel: __("Huawei NDP"),
                        },
                        {
                          name: "enable_box_discovery_mikrotik_ndp",
                          xtype: "checkboxfield",
                          boxLabel: __("MikroTik NDP"),
                        },
                        {
                          name: "enable_box_discovery_fdp",
                          xtype: "checkboxfield",
                          boxLabel: __("FDP"),
                        },
                        {
                          name: "enable_box_discovery_lldp",
                          xtype: "checkboxfield",
                          boxLabel: __("LLDP"),
                        },
                        {
                          name: "enable_box_discovery_oam",
                          xtype: "checkboxfield",
                          boxLabel: __("OAM"),
                        },
                        {
                          name: "enable_box_discovery_rep",
                          xtype: "checkboxfield",
                          boxLabel: __("REP"),
                        },
                        {
                          name: "enable_box_discovery_stp",
                          xtype: "checkboxfield",
                          boxLabel: __("STP"),
                        },
                        {
                          name: "enable_box_discovery_udld",
                          xtype: "checkboxfield",
                          boxLabel: __("UDLD"),
                        },
                        {
                          name: "enable_box_discovery_lacp",
                          xtype: "checkboxfield",
                          boxLabel: __("LACP"),
                        },
                        {
                          name: "enable_box_discovery_xmac",
                          xtype: "checkboxfield",
                          boxLabel: __("xMAC"),
                        },
                        {
                          name: "enable_box_discovery_ifdesc",
                          xtype: "checkboxfield",
                          boxLabel: __("IfDesc"),
                          reference: "enableBoxDiscoveryIfDesc",
                        },
                      ],
                    },
                    {
                      xtype: "container",
                      layout: "hbox",
                      defaults: {
                        padding: "0 8 0 0",
                      },
                      items: [
                        {
                          name: "neighbor_cache_ttl",
                          xtype: "numberfield",
                          tooltip: __("Cache neighbors (get_X_neighbors script result). <br/>" +
                                                        "When information cached script not execute on device <br/>" +
                                                        "0 - do not cache"),
                          fieldLabel: __("Cache neighbors for"),
                          allowBlank: false,
                          labelWidth: 250,
                          minValue: 0,
                          uiStyle: "small",
                          align: "right",
                          listeners: {
                            render: me.addTooltip,
                          },
                        },
                        {
                          xtype: "displayfield",
                          name: "_neighbor_cache_ttl",
                          value: __("sec"),
                        },
                      ],
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("IfDesc Policy"),
                  layout: "hbox",
                  defaults: {
                    padding: 4,
                    labelAlign: "right",
                  },
                  items: [
                    {
                      name: "ifdesc_symmetric",
                      xtype: "checkbox",
                      boxLabel: __("Symmetric Check"),
                      bind: {
                        disabled: "{!enableBoxDiscoveryIfDesc.checked}",
                      },
                    },
                    {
                      name: "ifdesc_patterns",
                      xtype: "inv.ifdescpatterns.LookupField",
                      fieldLabel: __("Patterns"),
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryIfDesc.checked}",
                      },
                    },
                    {
                      name: "ifdesc_handler",
                      xtype: "main.handler.LookupField",
                      fieldLabel: __("Handler"),
                      allowBlank: true,
                      query: {
                        allow_ifdesc: true,
                      },
                      bind: {
                        disabled: "{!enableBoxDiscoveryIfDesc.checked}",
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Platform & Version"),
                  items: [
                    {
                      name: "new_platform_creation_policy",
                      xtype: "combobox",
                      tooltip: __("Action when discovery new platform on version discovery. <br/>" +
                                                "Create - Create platform and set it on device<br/>" +
                                                "Alarm - Do not create platform and raise alarm"),
                      fieldLabel: __("On New Platform"),
                      labelWidth: 250,
                      store: [
                        ["C", __("Create")],
                        ["A", __("Alarm")],
                      ],
                      uiStyle: "medium",
                      allowBlank: false,
                      bind: {
                        disabled: "{!enableBoxDiscoveryVersion.checked}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                    {
                      name: "denied_firmware_policy",
                      xtype: "combobox",
                      tooltip: __("Action when discovery firmware denied on FirmwarePolice." +
                                                "Inventory -> Setup -> FirmwarePolicy <br/>" +
                                                "Ignore - Ignore and do next discovery<br/>" +
                                                "Ignore&Stop - Ignore and stop discovery<br/>" +
                                                "Raise Alarm - Raise alarm on ManagedObject and do next discovery<br/>" +
                                                "Raise Alarm&Stop - Raise alarm on ManagedObject and stop discovery"),
                      fieldLabel: __("On Denied Firmware"),
                      store: [
                        ["I", __("Ignore")],
                        ["s", __("Ignore&Stop")],
                        ["A", __("Raise Alarm")],
                        ["S", __("Raise Alarm&Stop")],
                      ],
                      labelWidth: 250,
                      uiStyle: "medium",
                      allowBlank: false,
                      bind: {
                        disabled: "{!enableBoxDiscoveryVersion.checked}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("VLAN"),
                  layout: {
                    type: "table",
                    columns: 3,
                  },
                  defaults: {
                    padding: "2px 4px 2px 4px",
                  },
                  items: [
                    {
                      xtype: "label",
                      text: __("Source"),
                    },
                    {
                      xtype: "label",
                      text: __("Enable"),
                    },
                    {
                      xtype: "label",
                      text: __("Policy"),
                    },
                    {
                      xtype: "label",
                      text: __("Interface"),
                    },
                    {
                      name: "vlan_interface_discovery",
                      xtype: "combobox",
                      store: [
                        ["D", __("Disable")],
                        ["S", __("State only")],
                        ["V", __("VLAN Sync")],
                      ],
                      allowBlank: true,
                      uiStyle: "medium",
                    },
                    {
                    },
                    {
                      xtype: "label",
                      text: __("Vlan DB"),
                    },
                    {
                      name: "vlan_vlandb_discovery",
                      xtype: "combobox",
                      store: [
                        ["D", __("Disable")],
                        ["S", __("State only")],
                        ["V", __("VLAN Sync")],
                      ],
                      allowBlank: true,
                      uiStyle: "medium",
                    },
                    {
                      name: "vlan_discovery_policy",
                      xtype: "combobox",
                      store: [
                        ["s", __("Script")],
                        ["S", __("Script, ConfDB")],
                        ["C", __("ConfDB, Script")],
                        ["c", __("ConfDB")],
                      ],
                      allowBlank: false,
                      uiStyle: "medium",
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("IPAM (VPN)"),
                  layout: {
                    type: "table",
                    columns: 3,
                  },
                  defaults: {
                    padding: "2px 4px 2px 4px",
                  },
                  items: [
                    {
                      xtype: "label",
                      text: __("Type"),
                    },
                    {
                      xtype: "label",
                      text: __("Enable"),
                    },
                    {
                      xtype: "label",
                      text: __("VPN Profile"),
                    },
                    {
                      xtype: "label",
                      text: __("Interface"),
                    },
                    {
                      name: "enable_box_discovery_vpn_interface",
                      xtype: "checkbox",
                      reference: "enableBoxDiscoveryVPNInterface",
                    },
                    {
                      name: "vpn_profile_interface",
                      xtype: "vc.vpnprofile.LookupField",
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryVPNInterface.checked}",
                      },
                    },
                    {
                      xtype: "label",
                      text: __("MPLS"),
                    },
                    {
                      name: "enable_box_discovery_vpn_mpls",
                      xtype: "checkbox",
                      reference: "enableBoxDiscoveryVPNMPLS",
                    },
                    {
                      name: "vpn_profile_mpls",
                      xtype: "vc.vpnprofile.LookupField",
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryVPNMPLS.checked}",
                      },
                    },
                    {
                      xtype: "label",
                      text: __("ConfDB"),
                    },
                    {
                      name: "enable_box_discovery_vpn_confdb",
                      xtype: "checkbox",
                      reference: "enableBoxDiscoveryVPNConfDB",
                    },
                    {
                      name: "vpn_profile_confdb",
                      xtype: "vc.vpnprofile.LookupField",
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryVPNConfDB.checked}",
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("IPAM (Prefix)"),
                  layout: {
                    type: "table",
                    columns: 3,
                  },
                  defaults: {
                    padding: "2px 4px 2px 4px",
                  },
                  items: [
                    {
                      xtype: "label",
                      text: __("Type"),
                    },
                    {
                      xtype: "label",
                      text: __("Enable"),
                    },
                    {
                      xtype: "label",
                      text: __("Prefix Profile"),
                    },
                    {
                      xtype: "label",
                      text: __("Interface"),
                    },
                    {
                      name: "enable_box_discovery_prefix_interface",
                      xtype: "checkbox",
                      reference: "enableBoxDiscoveryPrefixInterface",
                    },
                    {
                      name: "prefix_profile_interface",
                      xtype: "ip.prefixprofile.LookupField",
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryPrefixInterface.checked}",
                      },
                    },
                    {
                      xtype: "label",
                      text: __("Neighbor"),
                    },
                    {
                      name: "enable_box_discovery_prefix_neighbor",
                      xtype: "checkbox",
                      reference: "enableBoxDiscoveryPrefixNeighbor",
                    },
                    {
                      name: "prefix_profile_neighbor",
                      xtype: "ip.prefixprofile.LookupField",
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryPrefixNeighbor.checked}",
                      },

                    },
                    {
                      xtype: "label",
                      text: __("ConfDB"),
                    },
                    {
                      name: "enable_box_discovery_prefix_confdb",
                      xtype: "checkbox",
                      reference: "enableBoxDiscoveryPrefixConfDB",
                    },
                    {
                      name: "prefix_profile_confdb",
                      xtype: "ip.prefixprofile.LookupField",
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryPrefixConfDB.checked}",
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("IPAM (Address)"),
                  layout: {
                    type: "table",
                    columns: 3,
                  },
                  defaults: {
                    padding: "2px 4px 2px 4px",
                  },
                  items: [
                    {
                      xtype: "label",
                      text: __("Type"),
                    },
                    {
                      xtype: "label",
                      text: __("Enable"),
                    },
                    {
                      xtype: "label",
                      text: __("Address Profile"),
                    },
                    {
                      xtype: "label",
                      text: __("Interface"),
                    },
                    {
                      name: "enable_box_discovery_address_interface",
                      xtype: "checkbox",
                      reference: "enableBoxDiscoveryAddressInterface",
                    },
                    {
                      name: "address_profile_interface",
                      xtype: "ip.addressprofile.LookupField",
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryAddressInterface.checked}",
                      },
                    },
                    {
                      xtype: "label",
                      text: __("Management"),
                    },
                    {
                      name: "enable_box_discovery_address_management",
                      xtype: "checkbox",
                      reference: "enableBoxDiscoveryAddressManagement",
                    },
                    {
                      name: "address_profile_management",
                      xtype: "ip.addressprofile.LookupField",
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryAddressManagement.checked}",
                      },
                    },
                    {
                      xtype: "label",
                      text: __("DHCP"),
                    },
                    {
                      name: "enable_box_discovery_address_dhcp",
                      xtype: "checkbox",
                      reference: "enableBoxDiscoveryAddressDHCP",
                    },
                    {
                      name: "address_profile_dhcp",
                      xtype: "ip.addressprofile.LookupField",
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryAddressDHCP.checked}",
                      },
                    },
                    {
                      xtype: "label",
                      text: __("Neighbor"),
                    },
                    {
                      name: "enable_box_discovery_address_neighbor",
                      xtype: "checkbox",
                      reference: "enableBoxDiscoveryAddressNeighbor",
                    },
                    {
                      name: "address_profile_neighbor",
                      xtype: "ip.addressprofile.LookupField",
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryAddressNeighbor.checked}",
                      },
                    },
                    {
                      xtype: "label",
                      text: __("ConfDB"),
                    },
                    {
                      name: "enable_box_discovery_address_confdb",
                      xtype: "checkbox",
                      reference: "enableBoxDiscoveryAddressConfDB",
                    },
                    {
                      name: "address_profile_confdb",
                      xtype: "ip.addressprofile.LookupField",
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryAddressConfDB.checked}",
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Clear links"),
                  layout: "hbox",
                  defaults: {
                    padding: "0 8 0 0",
                  },
                  items: [
                    {
                      name: "clear_links_on_platform_change",
                      xtype: "checkboxfield",
                      boxLabel: __("On platform change"),
                    },
                    /* Not implemented yet
                                        {
                                            name: "clear_links_on_serial_change",
                                            xtype: "checkboxfield",
                                            boxLabel: __("On serial change")
                                        } */
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("SLA"),
                  layout: "hbox",
                  defaults: {
                    padding: "0 8 0 0",
                  },
                  items: [
                    {
                      name: "enable_box_discovery_sla",
                      xtype: "checkboxfield",
                      boxLabel: __("SLA"),
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("NRI"),
                  layout: "hbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "enable_box_discovery_nri_portmap",
                      xtype: "checkboxfield",
                      boxLabel: __("Portmapper"),
                      reference: "enableBoxDiscoveryNRIPortmap",
                    },
                    {
                      name: "enable_box_discovery_nri_service",
                      xtype: "checkboxfield",
                      boxLabel: __("Service Binding"),
                      bind: {
                        disabled: "{!enableBoxDiscoveryNRIPortmap.checked}",
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Housekeeping"),
                  layout: "hbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "enable_box_discovery_hk",
                      xtype: "checkboxfield",
                      boxLabel: __("Housekeeping"),
                      reference: "enableBoxDiscoveryHK",
                    },
                    {
                      name: "hk_handler",
                      xtype: "main.handler.LookupField",
                      fieldLabel: __("Handler"),
                      allowBlank: true,
                      uiStyle: "medium",
                      query: {
                        allow_housekeeping: true,
                      },
                      bind: {
                        disabled: "{!enableBoxDiscoveryHK.checked}",
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  layout: "hbox",
                  title: __("Discovery Alarm"),
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "box_discovery_alarm_policy",
                      xtype: "combobox",
                      fieldLabel: __("Box Alarm"),
                      allowBlank: true,
                      labelWidth: 150,
                      labelAlign: "left",
                      uiStyle: "small",
                      store: [
                        ["E", __("Enable")],
                        ["D", __("Disable")],
                      ],
                      value: "D",
                    },
                    {
                      name: "box_discovery_fatal_alarm_weight",
                      xtype: "numberfield",
                      fieldLabel: __("Fatal Alarm Weight"),
                      labelWidth: 150,
                      labelAlign: "left",
                      allowBlank: true,
                      minValue: 0,
                      uiStyle: "small",
                    },
                    {
                      name: "box_discovery_alarm_weight",
                      xtype: "numberfield",
                      fieldLabel: __("Alarm Weight"),
                      labelWidth: 150,
                      labelAlign: "left",
                      allowBlank: true,
                      minValue: 0,
                      uiStyle: "small",
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  layout: "hbox",
                  title: __("Process Telemetry"),
                  defaults: {
                    labelAlign: "left",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "box_discovery_telemetry_sample",
                      xtype: "numberfield",
                      tooltip: __("Sampling value for Box discovery. Interval from 0 to 1. <br/>" +
                                                "1 - all jobs will saved, 0 - Not collect telemetry, <br/>" +
                                                " 0,99 ... 0,1 - chance to save"),
                      labelWidth: 150,
                      minValue: 0,
                      maxValue: 1,
                      fieldLabel: __("Box Sample"),
                      allowBlank: true,
                      uiStyle: "small",
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                  ],
                },
              ],
            },
            {
              title: __("Periodic discovery"),
              items: [
                {
                  xtype: "container",
                  layout: "hbox",
                  items: [
                    {
                      name: "enable_periodic_discovery",
                      xtype: "checkbox",
                      boxLabel: __("Enable"),
                    },
                    {
                      name: "periodic_discovery_running_policy",
                      xtype: "combobox",
                      fieldLabel: __("Running Policy"),
                      store: [
                        ["R", __("Require Up")],
                        ["r", __("Require Up if ping enabled")],
                        ["i", __("Always Run")],
                      ],
                      allowBlank: false,
                      uiStyle: "medium",
                      padding: "0 0 0 4px",
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Periodic discovery intervals"),
                  layout: "vbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      xtype: "container",
                      layout: "hbox",
                      defaults: {
                        padding: "0 8 0 0",
                      },
                      items: [
                        {
                          name: "periodic_discovery_interval",
                          xtype: "numberfield",
                          fieldLabel: __("Interval, sec"),
                          allowBlank: false,
                          uiStyle: "small",
                          minValue: 0,
                          listeners: {
                            scope: me,
                            change: function(_item, newValue){
                              me.form.findField("periodic_discovery_interval_calculated").setValue(newValue);
                            },
                          },
                        },
                        {
                          name: "periodic_discovery_interval_calculated",
                          xtype: "displayfield",
                          renderer: NOC.render.Duration,
                        },
                      ],
                    },
                  ],
                },
                {
                  xtype: "container",
                  layout: {
                    type: "table",
                    columns: 3,
                  },
                  defaults: {
                    padding: "4 8 0 0",
                  },
                  items: [
                    {
                      name: "enable_periodic_discovery_uptime",
                      xtype: "checkboxfield",
                      boxLabel: __("Uptime"),
                      colspan: 2,
                    },
                    {
                      name: "periodic_discovery_uptime_interval",
                      xtype: "numberfield",
                      fieldLabel: __("Interval, sec"),
                      uiStyle: "small",
                      minValue: 0,
                    },
                    {
                      name: "enable_periodic_discovery_interface_status",
                      xtype: "checkboxfield",
                      boxLabel: __("Interface status"),
                      colspan: 2,
                    },
                    {
                      name: "periodic_discovery_interface_status_interval",
                      xtype: "numberfield",
                      fieldLabel: __("Interval, sec"),
                      uiStyle: "small",
                      minValue: 0,
                    },
                    {
                      name: "enable_periodic_discovery_mac",
                      xtype: "checkboxfield",
                      boxLabel: __("MAC"),
                      reference: "enablePeriodicDiscoveryMAC",
                      colspan: 3,
                    },
                    {
                      name: "periodic_discovery_mac_interval",
                      xtype: "numberfield",
                      fieldLabel: __("Interval, sec"),
                      uiStyle: "small",
                      minValue: 0,
                    },
                    {
                      name: "periodic_discovery_mac_filter_policy",
                      xtype: "combobox",
                      fieldLabel: __("Policy"),
                      store: [
                        ["A", __("All")],
                        ["I", __("Interface Profile")],
                      ],
                      tooltip: __("I - Collect MACs only for allowed interfaces. <br/>" +
                                        "(MAC Discovery Policy on Inventory -> Setup -> Interface Profile) <br/>") +
                                            "A - Collect All MACs",
                      allowBlank: false,
                      bind: {
                        disabled: "{!enablePeriodicDiscoveryMAC.checked}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },
                      uiStyle: "medium",
                    },
                    {
                      name: "mac_collect_vlanfilter",
                      xtype: "vc.vlanfilter.LookupField",
                      tooltip: __("Set which CAPS will be check in Caps discovery. <br/>" +
                                                "VC -> Setup -> VLAN Filter"),
                      fieldLabel: __("VLAN Filter"),
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryMAC.checked}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                    {
                      name: "enable_periodic_discovery_alarms",
                      xtype: "checkboxfield",
                      boxLabel: __("Alarms"),
                      colspan: 2,
                    },
                    {
                      name: "periodic_discovery_alarms_interval",
                      xtype: "numberfield",
                      fieldLabel: __("Interval,sec"),
                      uiStyle: "small",
                      minValue: 0,
                    },
                    {
                      name: "enable_periodic_discovery_cpestatus",
                      xtype: "checkboxfield",
                      boxLabel: __("CPE status"),
                      reference: "enablePeriodicDiscoveryCPEStatus",
                      colspan: 2,
                    },
                    {
                      name: "periodic_discovery_cpestatus_interval",
                      xtype: "numberfield",
                      fieldLabel: __("Interval,sec"),
                      uiStyle: "small",
                      minValue: 0,
                    },
                    {
                      name: "enable_periodic_discovery_peerstatus",
                      xtype: "checkboxfield",
                      boxLabel: __("Peer Status"),
                      colspan: 2,
                    },
                    {
                      name: "periodic_discovery_peerstatus_interval",
                      xtype: "numberfield",
                      fieldLabel: __("Interval, sec"),
                      uiStyle: "small",
                      minValue: 0,
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  layout: "hbox",
                  title: __("Discovery Alarm"),
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "periodic_discovery_alarm_policy",
                      xtype: "combobox",
                      fieldLabel: __("Periodic Alarm"),
                      allowBlank: true,
                      labelWidth: 135,
                      labelAlign: "left",
                      uiStyle: "medium",
                      store: [
                        ["E", __("Enable")],
                        ["D", __("Disable")],
                      ],
                      value: "D",
                    },
                    {
                      name: "periodic_discovery_fatal_alarm_weight",
                      xtype: "numberfield",
                      fieldLabel: __("Fatal Alarm Weight"),
                      labelWidth: 150,
                      labelAlign: "left",
                      allowBlank: true,
                      minValue: 0,
                      uiStyle: "small",
                    },
                    {
                      name: "periodic_discovery_alarm_weight",
                      xtype: "numberfield",
                      fieldLabel: __("Alarm Weight"),
                      labelWidth: 80,
                      labelAlign: "left",
                      allowBlank: true,
                      minValue: 0,
                      uiStyle: "small",
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  layout: "hbox",
                  title: __("Process Telemetry"),
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "periodic_discovery_telemetry_sample",
                      xtype: "numberfield",
                      tooltip: __("Sampling value for Periodic discovery. Interval from 0 to 1. <br/>" +
                                                "1 - all jobs will saved, 0 - Not collect telemetry, " +
                                                " 0,99 ... 0,1 - chance to save"),
                      labelWidth: 150,
                      minValue: 0,
                      maxValue: 1,
                      fieldLabel: __("Periodic Sample"),
                      allowBlank: true,
                      uiStyle: "medium",
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                  ],
                },
              ],
            },
            {
              title: __("Config"),
              tooltip: __("Settings policy for config discovery: Validation and mirroring config"),
              items: [
                {
                  xtype: "fieldset",
                  title: __("Config Policy"),
                  layout: "hbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "config_policy",
                      xtype: "combobox",
                      reference: "configPolicy",
                      fieldLabel: __("Config Policy"),
                      allowBlank: false,
                      tooltip: __("Select method of config gathering"),
                      displayField: "label",
                      valueField: "id",
                      store: {
                        fields: ["id", "label"],
                        data: [
                          {"id": "s", "label": __("Script")},
                          {"id": "S", "label": __("Script, Download")},
                          {"id": "D", "label": __("Download, Script")},
                          {"id": "d", "label": __("Download")},
                        ],
                      },
                      bind: {
                        disabled: "{!enableBoxDiscoveryConfig.checked}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                    {
                      name: "config_download_storage",
                      xtype: "main.extstorage.LookupField",
                      fieldLabel: __("Storage"),
                      query: {
                        type: "config_upload",
                      },
                      allowBlank: true,
                      tooltip: __("External storage for config downloading. " +
                                                "Setup in Main -> Setup -> Ext. storage"),
                      bind: {
                        disabled: "{disableConfigPolicy}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                    {
                      name: "config_download_template",
                      xtype: "main.template.LookupField",
                      fieldLabel: __("Path Template"),
                      allowBlank: true,
                      tooltip: __("Save config path template. " +
                                                "Setup on Main -> Setup -> Templates, subject form." +
                                                "Simple is: {{ object.name }}.txt on subject or <br/>" +
                                                '{{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}} for time'),
                      bind: {
                        disabled: "{disableConfigPolicy}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Config Fetching"),
                  layout: "hbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "config_fetch_policy",
                      xtype: "combobox",
                      fieldLabel: __("Config Fetch Policy"),
                      allowBlank: false,
                      displayField: "label",
                      valueField: "id",
                      store: {
                        fields: ["id", "label"],
                        data: [
                          ["s", __("Prefer Startup")],
                          ["r", __("Prefer Running")],
                        ],
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Config Mirror"),
                  layout: "hbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "config_mirror_policy",
                      xtype: "combobox",
                      reference: "mirrorPolicy",
                      fieldLabel: __("Mirror Policy"),
                      allowBlank: false,
                      tooltip: __("Mirror collected config after Config discovery. <br/>" +
                                                "Always Mirror - mirror every discovery run <br/>" +
                                                "Mirror on Change - save only if detect config changed"),
                      displayField: "label",
                      valueField: "id",
                      store: {
                        fields: ["id", "label"],
                        data: [
                          {"id": "D", "label": __("Disabled")},
                          {"id": "A", "label": __("Always Mirror")},
                          {"id": "C", "label": __("Mirror on Change")},
                        ],
                      },
                      bind: {
                        disabled: "{!enableBoxDiscoveryConfig.checked}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },

                    },
                    {
                      name: "config_mirror_storage",
                      xtype: "main.extstorage.LookupField",
                      fieldLabel: __("Storage"),
                      query: {
                        type: "config_mirror",
                      },
                      allowBlank: true,
                      tooltip: __("External storage for config save. " +
                                                "Setup in Main -> Setup -> Ext. storage"),
                      bind: {
                        disabled: "{disableConfigMirrorPolicy}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                    {
                      name: "config_mirror_template",
                      xtype: "main.template.LookupField",
                      fieldLabel: __("Path Template"),
                      allowBlank: true,
                      tooltip: __("Save config path template. " +
                                                "Setup on Main -> Setup -> Templates, subject form." +
                                                "Simple is: {{ object.name }}.txt on subject or <br/>" +
                                                '{{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}} for time'),
                      bind: {
                        disabled: "{disableConfigMirrorPolicy}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("ConfDB"),
                  layout: "hbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "confdb_raw_policy",
                      xtype: "combobox",
                      fieldLabel: __("Raw Policy"),
                      allowBlank: false,
                      store: [
                        ["D", __("Disabled")],
                        ["E", __("Enabled")],
                      ],
                      tooltip: __("Append raw section to confdb"),
                      bind: {
                        disabled: "{!enableBoxDiscoveryConfig.checked}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Config Validation"),
                  layout: "hbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "config_validation_policy",
                      xtype: "combobox",
                      fieldLabel: __("Validation Policy"),
                      allowBlank: false,
                      store: [
                        ["D", __("Disabled")],
                        ["A", __("Always Validate")],
                        ["C", __("Validate on Change")],
                      ],
                      tooltip: __("Run config validate process: <br/>" +
                                                "Always Validate - every discovery run<br/>" +
                                                "Validate on Change - only if detect config changed"),
                      bind: {
                        disabled: "{!enableBoxDiscoveryConfig.checked}",
                      },
                      listeners: {
                        render: me.addTooltip,
                      },
                    },
                    {
                      name: "object_validation_policy",
                      xtype: "cm.objectvalidationpolicy.LookupField",
                      fieldLabel: __("Policy"),
                      allowBlank: true,
                      bind: {
                        disabled: "{!enableBoxDiscoveryConfig.checked}",
                      },
                    },
                  ],
                },
                {
                  xtype: "fieldset",
                  title: __("Beef"),
                  layout: "hbox",
                  defaults: {
                    labelAlign: "top",
                    padding: 4,
                  },
                  items: [
                    {
                      name: "beef_policy",
                      xtype: "combobox",
                      reference: "beefPolicy",
                      fieldLabel: __("Beef Policy"),
                      allowBlank: false,
                      displayField: "label",
                      valueField: "id",
                      store: {
                        fields: ["id", "label"],
                        data: [
                          {"id": "D", "label": __("Disabled")},
                          {"id": "A", "label": __("Always Collect")},
                          {"id": "C", "label": __("Collect on Change")},
                        ],
                      },
                    },
                    {
                      name: "beef_storage",
                      xtype: "main.extstorage.LookupField",
                      fieldLabel: __("Storage"),
                      query: {
                        type: "beef",
                      },
                      allowBlank: true,
                      bind: {
                        disabled: "{disableBeefPolicy}",
                      },
                    },
                    {
                      name: "beef_path_template",
                      xtype: "main.template.LookupField",
                      fieldLabel: __("Path Template"),
                      allowBlank: true,
                      bind: {
                        disabled: "{disableBeefPolicy}",
                      },
                    },
                  ],
                },
              ],
              listeners: {
                render: me.addTooltip,
              },
            },
            {
              title: __("Metrics"),
              tooltip: __("Setup colleted metric on devices (not Interface!). <br/>" +
                                "(Interface Metrics settings Inventory -> Setup -> Interface Profile)"),
              items: [
                {
                  name: "enable_metrics",
                  xtype: "checkboxfield",
                  boxLabel: __("Enable Metrics"),
                },
                {
                  xtype: "container",
                  layout: "hbox",
                  defaults: {
                    padding: "0 8 0 0",
                  },
                  items: [
                    {
                      name: "metrics_default_interval",
                      xtype: "numberfield",
                      fieldLabel: __("Default Interval, sec"),
                      labelWidth: 200,
                      allowBlank: false,
                      uiStyle: "small",
                      minValue: 0,
                      listeners: {
                        scope: me,
                        change: function(_item, newValue){
                          me.form.findField("metrics_default_interval_calculated").setValue(newValue);
                        },
                      },
                    },
                    {
                      name: "metrics_default_interval_calculated",
                      xtype: "displayfield",
                      renderer: NOC.render.Duration,
                    },
                  ],
                },
                {
                  name: "metrics",
                  xtype: "gridfield",
                  fieldLabel: __("Metrics"),
                  labelAlign: "top",
                  columns: [
                    {
                      text: __("Metric Type"),
                      dataIndex: "metric_type",
                      width: 150,
                      editor: {
                        xtype: "pm.metrictype.LookupField",
                      },
                      renderer: NOC.render.Lookup("metric_type"),
                    },
                    {
                      text: __("Is Stored"),
                      dataIndex: "is_stored",
                      width: 50,
                      renderer: NOC.render.Bool,
                      editor: "checkbox",
                    },
                    {
                      text: __("Interval"),
                      dataIndex: "interval",
                      editor: {
                        xtype: "numberfield",
                        minValue: 0,
                      },
                    },
                  ],

                },
              ],
              listeners: {
                render: me.addTooltip,
              },
            },
            {
              title: __("Autosegmentation"),
              tooltip: __("Settings for autosegmentation process: <br/>" +
                                "Automatically detect segment for ManagedObject with this ObjectProfile.<br/>" +
                                "Uses MAC and needed MAC enable in Box"),
              items: [
                {
                  name: "autosegmentation_policy",
                  xtype: "combobox",
                  labelWidth: 150,
                  fieldLabel: __("Policy"),
                  allowBlank: false,
                  store: [
                    ["d", __("Do not segmentate")],
                    ["e", __("Allow autosegmentation")],
                    ["o", __("Segmentate for object's segment")],
                    ["c", __("Segmentate for child segment")],
                  ],
                  uiStyle: "medium",
                },
                {
                  name: "autosegmentation_level_limit",
                  xtype: "numberfield",
                  tooltip: __("Max level (Common -> Level) there will be changed segment. <br/>" +
                                        "(Autosegmentation not worked with ManagedObject less this level"),
                  labelWidth: 150,
                  fieldLabel: __("Level Limit"),
                  allowBlank: false,
                  uiStyle: "small",
                  listeners: {
                    render: me.addTooltip,
                  },
                },
                {
                  name: "autosegmentation_segment_name",
                  xtype: "textfield",
                  tooltip: __("Jinja template for creating segment name. <br/>" +
                                        "Worked with \"Segmentate for object's segment\" and " +
                                        "\"Segmentate for child segment\" options"),
                  labelWidth: 150,
                  fieldLabel: __("Segment Name"),
                  allowBlank: true,
                  uiStyle: "extra",
                  listeners: {
                    render: me.addTooltip,
                  },
                },
              ],
              listeners: {
                render: me.addTooltip,
              },
            },
          ],
        },
      ],
      formToolbar: [],
    });
    me.callParent();
  },
  //
  filters: [
    {
      title: __("Box Discovery"),
      ftype: "list",
      listStore: {
        sorters: "label",
        data: [
          {field_name: "enable_box_discovery_profile", label: __("Profile")},
          {field_name: "enable_box_discovery_version", lLabel: __("Version")},
          {field_name: "enable_box_discovery_caps", label: __("Caps")},
          {field_name: "enable_box_discovery_interface", label: __("Interface")},
          {field_name: "enable_box_discovery_prefix", label: __("Prefix")},
          {field_name: "enable_box_discovery_id", label: __("ID")},
          {field_name: "enable_box_discovery_config", label: __("Config")},
          {field_name: "enable_box_discovery_asset", label: __("Asset")},
          {field_name: "enable_box_discovery_vlan", label: __("VLAN")},
          {field_name: "enable_box_discovery_metrics", label: __("Metrics")},
        ],
      },
      valuesStore: {
        sorters: "label",
        data: [
          {label: __("Enabled"), value: true},
          {label: __("Disabled"), value: false},
          {label: __("All"), value: "all"},
        ],
      },
    },
    {
      title: __("Topology Discovery"),
      ftype: "list",
      listStore: {
        sorters: "label",
        data: [
          {field_name: "enable_box_discovery_nri", label: __("NRI")},
          {field_name: "enable_box_discovery_bfd", label: __("BFD")},
          {field_name: "enable_box_discovery_cdp", label: __("CDP")},
          {field_name: "enable_box_discovery_huawei_ndp", label: __("Huawei NDP")},
          {field_name: "enable_box_discovery_mikrotik_ndp", label: __("MikroTik NDP")},
          {field_name: "enable_box_discovery_fdp", label: __("FDP")},
          {field_name: "enable_box_discovery_lldp", label: __("LLDP")},
          {field_name: "enable_box_discovery_oam", label: __("OAM")},
          {field_name: "enable_box_discovery_rep", label: __("REP")},
          {field_name: "enable_box_discovery_stp", label: __("STP")},
          {field_name: "enable_box_discovery_udld", label: __("UDLD")},
          {field_name: "enable_box_discovery_lacp", label: __("LACP")},
        ],
      },
      valuesStore: {
        sorters: "label",
        data: [
          {label: __("Enabled"), value: true},
          {label: __("Disabled"), value: false},
          {label: __("All"), value: "all"},
        ],
      },
    },
    {
      title: __("Periodic Discovery"),
      ftype: "list",
      listStore: {
        sorters: "label",
        data: [
          {field_name: "enable_periodic_discovery_uptime", label: __("Uptime")},
          {field_name: "enable_periodic_discovery_interface_status", label: __("Interface status")},
          {field_name: "enable_periodic_discovery_mac", label: __("MAC")},
          {field_name: "enable_periodic_discovery_metrics", label: __("Metrics")},
        ],
      },
      valuesStore: {
        sorters: "label",
        data: [
          {label: __("Enabled"), value: true},
          {label: __("Disabled"), value: false},
          {label: __("All"), value: "all"},
        ],
      },
    },
  ],
  //
  cleanData: function(v){
    Ext.each(v.metrics, function(m){
      if(m.low_error === ""){
        m.low_error = null;
      }
      if(m.low_warn === ""){
        m.low_warn = null;
      }
      if(m.high_warn === ""){
        m.high_warn = null;
      }
      if(m.high_error === ""){
        m.high_error = null;
      }
    });
  },
});
