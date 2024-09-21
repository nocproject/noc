//---------------------------------------------------------------------
// inv.inv PConf Controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.pconf.Controller");

Ext.define("NOC.inv.inv.plugins.pconf.Controller", {
  extend: "Ext.app.ViewController",
  alias: "controller.pconf",

  onDataChanged: function(store){
    var vm = this.getViewModel(),
      hasStatus = store.findBy(function(record){
        return !Ext.isEmpty(record.get("status"));
      }) === -1;
    
    if(vm){
      vm.set("totalCount", store.getCount());
    }
    vm.set("statusDisabled", hasStatus);
  },
  onReload: function(){
    var me = this;
    me.getView().mask(__("Loading..."));
    Ext.Ajax.request({
      url: "/inv/inv/" + me.getView().currentId + "/plugin/pconf/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText),
          view = me.getView();
        view.preview(data);
        view.unmask();
      },
      failure: function(){
        NOC.error(__("Failed to load data"));
        me.getView().unmask();
      },
    });
  },
  onValueChanged: function(data){
    var me = this;
    Ext.Ajax.request({
      url: "/inv/inv/" + this.getView().currentId + "/plugin/pconf/set/",
      method: 'POST',
      jsonData: data,
      success: function(response){
        var data = Ext.decode(response.responseText);
        if(data.status){
          NOC.info(__("Parameter has been set"));
          me.getView().down("grid").findPlugin("valueedit").cancelEdit();
          me.onReload();
        } else{
          NOC.error(data.message);
        }
      },
      failure: function(){
        NOC.error(__("Failed to set parameter"));
      },
    });
  },
  onStatusChange: function(group, button){
    var store = this.getViewModel().getStore("gridStore"),
      filters = store.getFilters();
    
    this.removeFilter();
    if(button.pressed){
      filters.add({
        id: "invConfigStatusFilter",
        filterFn: function(record){
          var status = record.get("status");
          return button.value === status
        },
      });
    }
  },
  onTabTypeChange: function(){
    this.removeFilter();
  },
  valueRenderer: function(value, metaData, record){
    var displayValue = value;
    if(record.get("type") === "enum"){
      var options = record.get("options") || [],
        option = options.find(opt => opt.id === value);
      displayValue = option ? option.label : value;
    }
    if(Ext.isEmpty(record.get("status"))){
      if(record.get("read_only")){
        return "<i class='fas fa fa-lock' style='padding-right: 4px;' title='" + __("Read only") + "'></i>" + displayValue;
      }
      return "<i class='fas fa fa-pencil' style='padding-right: 4px;'></i>" + displayValue; 
    }

    var val = this.whichRange(value, record.get("thresholds")),
      result = `<div data-value='${value}' class='noc-metric-value' style='left: ${val}%'></div>`
    + "<div class='noc-metric-container'>"
      + "<div class='noc-metric-range noc-metric-green-range'></div>";
    
    if(!Ext.isEmpty(record.get("status"))){
      var ticks = this.zip(record.get("thresholds"), [20, 40, 60, 80]),
        ranges = this.zip([[0,20], [20,40], [40,60], [60,80], [80,100]], ["red", "yellow", "green", "yellow", "red"]);
      
      Ext.each(ranges, function(range){
        result += `<div class='noc-metric-range' style='left:  ${range[0][0]}%; width: ${range[0][1]}%; background: ${range[1]};'></div>`;
      });
      Ext.each(ticks, function(tick){
        result += `<div class='noc-metric-tick' data-qtip='${tick[0]}' style='left: ${tick[1]}%'></div>`;
      });
    }
    result += "</div>";
    if(record.get("read_only")){
      return "<i class='fas fa fa-lock' style='padding-right: 4px;' title='" + __("Read only") + "'></i>" + result; 
    }
    return "<i class='fas fa fa-pencil' style='padding-right: 4px;'></i>" + result;
  },
  whichRange: function(value, ranges){
    var val = parseFloat(value);
    if(Ext.isEmpty(ranges) || ranges.filter(range => Ext.isEmpty(range)).length > 0){
      return 50;
    }
    if(val < parseFloat(ranges[0])){
      return 10;
    } else if(val < parseFloat(ranges[1])){
      return 30;
    } else if(val < parseFloat(ranges[2])){
      return 50;
    } else if(val < parseFloat(ranges[3])){
      return 60;
    } else{
      return 80;
    }
  },
  zip: function(){
    var args = Array.prototype.slice.call(arguments),
      length = Math.max.apply(null, args.map(function(arr){ return arr.length; })),
      result = [];

    for(var i = 0; i < length; i++){
      var row = args.map(function(arr){ return arr[i]; });
      result.push(row);
    }

    return result;
  },
  removeFilter: function(){
    var store = this.getViewModel().getStore("gridStore"),
      filters = store.getFilters(),
      statusFilter = filters.find("_id", "invConfigStatusFilter");

    this.getViewModel().set("status", null);
    if(statusFilter){
      filters.remove(statusFilter);
    }
  },
});
