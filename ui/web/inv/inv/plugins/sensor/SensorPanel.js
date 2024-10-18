//---------------------------------------------------------------------
// inv.inv SensorPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.sensor.SensorPanel");

Ext.define("NOC.inv.inv.plugins.sensor.SensorPanel", {
  extend: "Ext.panel.Panel",
  title: __("Sensors"),
  closable: false,
  layout: "fit",
  requires: [
    "NOC.core.StateField",
    "NOC.inv.sensorprofile.LookupField",
    "NOC.pm.measurementunits.LookupField",
    "Ext.ux.form.GridField",
  ],

  initComponent: function(){
    var me = this;

    me.gridField = Ext.create({
      xtype: "gridfield",
      columns: [
        {
          dataIndex: "local_id",
          text: __("Name"),
        },
        {
          dataIndex: "profile",
          text: __("Profile"),
          renderer: NOC.render.Lookup("profile"),
          editor: {
            xtype: "inv.sensorprofile.LookupField",
          },
        },
        {
          dataIndex: "units",
          text: __("Units"),
          renderer: NOC.render.Lookup("units"),
          editor: {
            xtype: "pm.measurementunits.LookupField",
          },
        },
        {
          dataIndex: "object__label",
          text: __("Object"),
          width: 220,
        },
        {
          dataIndex: "state",
          text: __("State"),
          renderer: NOC.render.Lookup("state"),
        },
        {
          dataIndex: "modbus_register",
          text: __("Modbus Register"),
        },
        {
          dataIndex: "modbus_format",
          text: __("Modbus Format"),
        },
        {
          dataIndex: "protocol",
          text: __("Protocol"),
        },
        {
          dataIndex: "snmp_oid",
          text: __("SNMP OID"),
          width: 200,
        },
      ],
      onCellEdit: function(editor, e){
        var data = {},
          grid = this.grid,
          ed = e.grid.columns[e.colIdx].getEditor();

        if(ed.rawValue){
          e.record.set(e.field + "__label", ed.rawValue);
        }
        data[e.field] = e.value;
        grid.mask(__("Saving ..."));
        Ext.Ajax.request({
          url: "/inv/inv/" + e.record.data.id + "/plugin/sensor/",
          method: "POST",
          scope: me,
          jsonData: data,
          success: function(){
            grid.unmask();
            e.record.commit();
            NOC.msg.complete(__("Saved"));
          },
          failure: function(response){
            var message = __("Not saved");
            if(response.responseText){
              try{
                message = Ext.decode(response.responseText).message
              } catch(err){
                console.log(response.responseText);
                console.error(err);
              }
            }
            grid.unmask();
            NOC.error(message)
          },
        });
      },
    });
    Ext.override(me.gridField, {
    });
    Ext.apply(me, {
      items: [
        me.gridField,
      ],
    });
    me.callParent();
  },
  //
  preview: function(data){
    var me = this;
    me.currentId = data.id;
    me.gridField.store.loadData(data)
  },
});
