//---------------------------------------------------------------------
// maintenance.maintenance application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintenance.maintenance.Application");

Ext.define("NOC.maintenance.maintenance.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.maintenance.maintenance.Model",
    "NOC.maintenance.maintenance.ObjectsPanel",
    "NOC.maintenance.maintenancetype.LookupField",
    "NOC.sa.managedobject.LookupField",
    "NOC.inv.networksegment.ComboTree",
    "NOC.main.timepattern.LookupField",
    "NOC.main.template.LookupField",
    "NOC.maintenance.maintenance.DirectObjectsModel",
    "NOC.maintenance.maintenance.DirectSegmentsModel",
    "NOC.core.filter.Filter",
  ],
  model: "NOC.maintenance.maintenance.Model",
  search: true,
  initComponent: function(){
    var me = this;

    me.ITEM_OBJECTS = me.registerItem(
      "NOC.maintenance.maintenance.ObjectsPanel",
    );

    me.cardButton = Ext.create("Ext.button.Button", {
      text: __("Card"),
      glyph: NOC.glyph.eye,
      scope: me,
      handler: me.onCard,
    });

    me.affectedButton = Ext.create("Ext.button.Button", {
      text: __("Affected Objects"),
      glyph: NOC.glyph.eye,
      scope: me,
      handler: me.onObjects,
    });

    Ext.apply(me, {
      columns: [
        {
          text: __("Type"),
          dataIndex: "type",
          width: 150,
          renderer: NOC.render.Lookup("type"),
        },
        {
          text: __("Start"),
          dataIndex: "start",
          width: 120,
        },
        {
          text: __("Stop"),
          dataIndex: "stop",
          width: 120,
        },
        {
          text: __("Completed"),
          dataIndex: "is_completed",
          width: 25,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Auto-confirm"),
          dataIndex: "auto_confirm",
          width: 25,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Time Pattern"),
          dataIndex: "time_pattern",
          width: 150,
          renderer: NOC.render.Lookup("time_pattern"),
        },
        {
          text: __("TT"),
          dataIndex: "escalation_tt",
          width: 150,
          sortable: false,
          renderer: function(v, _, record){
            var r = [],
              tt = record.get("escalation_tt") || false,
              ee = record.get("escalation_error") || false;
            if(tt){
              r.push('<a href="/api/card/view/tt/' + tt + '/" target="_blank">' + tt + "</a>");
            } else{
              if(ee){
                r.push('<i class="fa fa-exclamation-triangle"></i> Error')
              }
            }
            return r;
          },
        },
        {
          text: __("Subject"),
          dataIndex: "subject",
          flex: 1,
        },
      ],
      fields: [
        {
          name: "subject",
          xtype: "textfield",
          fieldLabel: __("Subject"),
          allowBlank: false,
        },
        {
          name: "type",
          xtype: "maintenance.maintenancetype.LookupField",
          fieldLabel: __("Type"),
          allowBlank: false,
        },
        {
          xtype: "container",
          layout: "hbox",
          items: [
            {
              name: "start_date",
              xtype: "datefield",
              startDay: 1,
              fieldLabel: __("Start"),
              allowBlank: false,
              format: "d.m.Y",
            },
            {
              name: "start_time",
              xtype: "timefield",
              allowBlank: false,
              labelWidth: 0,
              format: "H:i",
            },
          ],
        },
        {
          xtype: "container",
          layout: "hbox",
          items: [
            {
              name: "stop_date",
              xtype: "datefield",
              startDay: 1,
              fieldLabel: __("Stop"),
              allowBlank: false,
              format: "d.m.Y",
            },
            {
              name: "stop_time",
              xtype: "timefield",
              allowBlank: false,
              labelWidth: 0,
              format: "H:i",
            },
          ],
        },
        {
          name: "is_completed",
          xtype: "checkbox",
          boxLabel: __("Completed"),
        },
        {
          name: "auto_confirm",
          xtype: "checkbox",
          boxLabel: __("Auto-confirm"),
        },
        {
          name: "template",
          xtype: "main.template.LookupField",
          fieldLabel: __("Close Template"),
          allowBlank: true,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "contacts",
          xtype: "textarea",
          fieldLabel: __("Contacts"),
          allowBlank: false,
        },
        {
          name: "time_pattern",
          xtype: "main.timepattern.LookupField",
          fieldLabel: __("Time Pattern"),
          allowBlank: true,
        },
        {
          name: "suppress_alarms",
          xtype: "checkbox",
          boxLabel: __("Suppress alarms"),
        },
        {
          name: "escalation_policy",
          xtype: "combobox",
          fieldLabel: __("Escalation Policy"),
          allowBlank: true,
          store: [
            ["E", __("Enable")],
            ["D", __("Disable")],
            ["S", __("Suspend")],
            ["M", __("Maintenance")],
          ],
          uiStyle: "medium",
          listeners: {
            change: function(field, value){
              this.nextSibling().setDisabled(value !== "M");
            },
          },
        },
        {
          name: "escalate_managed_object",
          xtype: "sa.managedobject.LookupField",
          fieldLabel: __("Escalate to"),
          allowBlank: true,
          disabled: true,
        },
      ],
      gridToolbar: [
        {
          xtype: "combo",
          fieldLabel: __("Status"),
          store: [
            ["false", __("Active")],
            ["true", __("Completed")],
          ],
          triggerAction: "all",
          editable: false,
          queryMode: "local",
          // ToDo need check
          hasAccess: function(app){
            return app.search === true;
          },
          triggers: {
            clear: {
              cls: "x-form-clear-trigger",
              hidden: true,
              weight: -1,
              handler: function(field){
                field.setValue(null);
                field.fireEvent("select", field);
              },
            },
          },
          listeners: {
            scope: me,
            select: function(field){
              var me = this,
                value = field.getValue();
              if(value){
                me.currentQuery.is_completed = value;
              } else{
                delete me.currentQuery.is_completed;
              }
              me.reloadStore();
            },
            change: function(field, value){
              if(value == null || value === ""){
                field.getTrigger("clear").hide();
                return;
              }
              field.getTrigger("clear").show();
            },
          },
        },
      ],
      formToolbar: [
        me.cardButton,
        me.affectedButton,
      ],
    });
    me.callParent();
  },
  inlines: [
    {
      title: __("Objects"),
      collapsed: false,
      model: "NOC.maintenance.maintenance.DirectObjectsModel",
      columns: [
        {
          text: __("Object"),
          dataIndex: "object",
          editor: "sa.managedobject.LookupField",
          flex: 1,
          renderer: NOC.render.Lookup("object"),
        },
      ],
    },
    {
      title: __("Segments"),
      collapsed: false,
      model: "NOC.maintenance.maintenance.DirectSegmentsModel",
      columns: [
        {
          text: __("Segment"),
          dataIndex: "segment",
          editor: "inv.networksegment.ComboTree",
          flex: 1,
          renderer: NOC.render.Lookup("segment"),
        },
      ],
    },
  ],
  ePolicy: function(){
    return true
  },

  editRecord: function(record){
    var me = this,
      start = Ext.Date.parse(record.get("start"), "Y-m-d H:i:s"),
      stop = Ext.Date.parse(record.get("stop"), "Y-m-d H:i:s");
    record.set("start_date", start);
    record.set("start_time", start);
    record.set("stop_date", stop);
    record.set("stop_time", stop);
    me.callParent([record]);
    me.cardButton.setDisabled(false);
    me.affectedButton.setDisabled(false);
  },

  cleanData: function(v){
    var me = this;
    me.callParent([v]);
    v.start = me.mergeDate(v.start_date, v.start_time);
    delete v.start_date;
    delete v.start_time;
    v.stop = me.mergeDate(v.stop_date, v.stop_time);
    delete v.stop_date;
    delete v.stop_time;
  },

  mergeDate: function(d, t){
    var year = d.getFullYear(),
      month = d.getMonth(),
      day = d.getDate(),
      hour = t.getHours(),
      min = t.getMinutes(),
      sec = t.getSeconds(),
      q = function(v){
        if(v < 10){
          return "0" + v;
        } else{
          return "" + v;
        }
      };
    return "" + year + "-" + q(month + 1) + "-" + q(day) + "T" +
            q(hour) + ":" + q(min) + ":" + q(sec);
  },

  onCard: function(){
    var me = this;
    if(me.currentRecord){
      window.open(
        "/api/card/view/maintenance/" + me.currentRecord.get("id") + "/",
      );
    }
  },

  onObjects: function(){
    var me = this;
    me.previewItem(me.ITEM_OBJECTS, me.currentRecord);
  },

  newRecord: function(defaults){
    var me = this;

    me.callParent([defaults]);
    me.cardButton.setDisabled(true);
    me.affectedButton.setDisabled(true);
  },
});
