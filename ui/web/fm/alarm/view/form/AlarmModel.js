//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.form.AlarmModel");

Ext.define("NOC.fm.alarm.view.form.AlarmModel", {
  extend: "Ext.app.ViewModel",
  alias: "viewmodel.fm.alarm.form",
  formulas: {
    alarmUrl: {
      bind: "{selected.id}",
      get: function(value){
        return "/fm/alarm/" + value;
      },
    },
    header: {
      bind: "{selected}",
      deep: true,
      get: function(value){
        var header = "<div class='noc-alarm-subject " + value.row_class + "'>"
                    + value.subject + " [" + value.severity__label + "/" + value.severity + "]"
                    + "<span class='noc-alarm-timestamp'>" + value.timestamp + " (" + value.duration + ")</span></div>"
                    + "<div>"
                    + "<span class='noc-alarm-label'>Object</span>" + value.managed_object__label
                    + "<span class='noc-alarm-label' style='padding-left: 5px'>IP</span>" + value.managed_object_address;
        if(Object.prototype.hasOwnProperty.call(value, "managed_object_platform")){
          header += "<span class='noc-alarm-label' style='padding-left: 5px'>Platform</span>" + value.managed_object_platform;
        }
        if(Object.prototype.hasOwnProperty.call(value, "managed_object_version")){
          header += "<span class='noc-alarm-label' style='padding-left: 5px'>Version</span>" + value.managed_object_version;
        }
        header += "</div>";
        if(Object.prototype.hasOwnProperty.call(value, "segment_path")){
          header += "<div><span class='noc-alarm-label'>Segment</span>" + value.segment_path + "</div>";
        }
        if(Object.prototype.hasOwnProperty.call(value, "container_path")){
          header += "<div><span class='noc-alarm-label'>Location</span>" + value.container_path + "</div>";
        }
        if(Object.prototype.hasOwnProperty.call(value, "address_path")){
          header += "<div><span class='noc-alarm-label'>Address</span>" + value.address_path + "</div>";
        }
        if(Object.prototype.hasOwnProperty.call(value, "ack_user") && value.ack_user){
          header += "<div><span class='noc-alarm-label'>Acknowledge</span>" + value.ack_user + " at " + value.ack_ts + "</div>";
        }
        return header;
      },
    },
    overviewPanel: {
      bind: "{selected}",
      deep: true,
      get: function(value){
        return "<div class='noc-tp'><b>" + value.subject + "</b><br/><pre>" + value.body + "</pre></div>";
      },
    },
    helpPanel: {
      bind: "{selected}",
      deep: true,
      get: function(value){
        return "<div class='noc-tp'><b>Symptoms:</b><br/><pre>" + value.symptoms + "</pre><br/><b>Probable Causes:</b><br/><pre>" + value.probable_causes + "</pre><br/><b>Recommended Actions:</b><br/><pre>" + value.recommended_actions + "</pre><br/></div>";
      },
    },
    dataPanel: {
      bind: "{selected}",
      deep: true,
      get: function(value){
        var html = "<div class='noc-tp'><table border='0'>",
          addTable = function(header, array){
            var html = "<tr><th colspan='2'>" + header + "</th></tr>";
            for(var i = 0; i < array.length; i++){
              html += "<tr><td><b>" + array[i][0] + "</b></td><td>" + array[i][1] + "</td></tr>";
            }
            return html;
          };
        if(!Ext.isEmpty(value.vars)){
          html += addTable("Alarm Variables", value.vars);
        }
        if(!Ext.isEmpty(value.raw_vars)){
          html += addTable("Resolved Variables", value.resolved_vars);
        }
        if(!Ext.isEmpty(value.resolved_vars)){
          html += addTable("Raw Variables", value.raw_vars);
        }
        html += "</table></div>";
        return html;
      },
    },
    isClosed: {
      bind: "{selected.status}",
      get: function(value){
        return value === "C";
      },
    },
    isNotActive: {
      bind: "{selected.status}",
      get: function(value){
        return value !== "A";
      },
    },
    isSubscribe: {
      bind: "{selected.subscribers}",
      get: function(value){
        return value.filter(function(user){
          return user.login === NOC.username;
        }).length > 0;
      },
    },
    isAcknowledge: {
      bind: "{selected.ack_user}",
      get: function(value){
        return value != null;
      },
    },
    isFavorite: {
      bind: "{selected.fav_status}",
      get: function(value){
        return value;
      },
    },
    favoriteText: {
      bind: "{selected.fav_status}",
      get: function(value){
        return (value == true) ? __("Remove from Favorites") : __("Add to Favorites");
      },
    }, 
    favIconCls: {
      bind: "{selected.fav_status}",
      get: function(value){
        return (value == true) ? "noc-starred" : "noc-unstarred";
      },
    },
    acknowledgeText: function(get){
      return get("isAcknowledge") ? get("selected.ack_user") : __("Ack");
    },
    isAcknowledgeDisabled: {
      bind: "{selected.status}",
      get: function(value){
        return !(this.getView().up().permissions["acknowledge"] && value === "A");
      },
    },
    hasVars: {
      bind: "{selected}",
      deep: true,
      get: function(value){
        return !Ext.isEmpty(value.vars) || !Ext.isEmpty(value.raw_vars) || !Ext.isEmpty(value.resolved_vars);
      },
    },
    hasAlarms: {
      bind: "{selected}",
      deep: true,
      get: function(value){
        return Object.prototype.hasOwnProperty.call(value, "alarms");
      },
    },
    selectedLog: {
      bind: "{selected.log}",
      deep: true,
      get: function(value){
        return {
          fields: [
            {
              name: "timestamp",
              type: "date",
            },
            "from_status", "to_status", "message",
          ],
          data: value,
        };
      },
    },
    selectedEvents: {
      bind: "{selected.events}",
      deep: true,
      get: function(value){
        return {
          fields: [
            {
              name: "id",
              type: "string",
            },
            {
              name: "status",
              type: "string",
            },
            {
              name: "managed_object",
              type: "int",
            },
            {
              name: "managed_object__label",
              type: "string",
            },
            {
              name: "event_class",
              type: "string",
            },
            {
              name: "event_class__label",
              type: "string",
            },
            {
              name: "timestamp",
              type: "date",
            },
            {
              name: "subject",
              type: "string",
            },
          ],
          data: value,
        };
      },
    },
    selectedAlarms: {
      bind: "{selected}",
      deep: true,
      get: function(value){
        var data = value.alarms;
        if(!Object.prototype.hasOwnProperty.call(value, "alarms")){
          data = {
            text: __("."),
            children: [],
          };
        }
        return {
          type: "tree",
          fields: [
            {
              name: "id",
              type: "string",
            },
            {
              name: "timestamp",
              type: "date",
            },
            {
              name: "subject",
              type: "string",
            },
            {
              name: "managed_object",
              type: "int",
            },
            {
              name: "managed_object__label",
              type: "string",
            },
            {
              name: "alarm_class",
              type: "string",
            },
            {
              name: "alarm_class__label",
              type: "string",
            },
            {
              name: "row_class",
              type: "string",
            },
          ],
          root: data,
        }
      },
    },
    selectedGroups: {
      bind: "{selected.groups}",
      deep: true,
      get: function(value){
        return {
          fields: [
            {
              name: "id",
              type: "string",
            },
            {
              name: "timestamp",
              type: "date",
            },
            {
              name: "subject",
              type: "string",
            },
            {
              name: "alarm_class",
              type: "string",
            },
            {
              name: "alarm_class__label",
              type: "string",
            },
          ],
          data: value,
        };
      },
    },
  },
});