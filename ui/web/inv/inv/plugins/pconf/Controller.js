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
      hasStatus = function(value){
        return store.findBy(function(record){
          return !Ext.isEmpty(record.get("status")) && record.get("status") === value;
        }) === -1;
      },
      hasStatuses = {
        u: hasStatus("u"),
        c: hasStatus("c"),
        w: hasStatus("w"),
        o: hasStatus("o"),
      };
    
    if(vm){
      vm.set("totalCount", store.getCount());
    }
    vm.set("statusDisabled", hasStatuses);
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
  onButtonRender: function(button){
    var config = this.getView().getStatus()[button.value];
    button.setGlyph("x" + NOC.glyph[config.glyph].toString(16));
    button.getEl().down(".x-btn-glyph").setStyle("color", config.color);
  },
  valueRenderer: function(value, metaData, record){
    var displayValue = value,
      allStatusConf = this.getView().getStatus(),
      status = record.get("status");
    if(record.get("type") === "enum"){
      var options = record.get("options") || [],
        option = options.find(opt => opt.id === value);
      displayValue = option ? option.label : value;
    }
    if(Ext.isEmpty(status)){
      if(record.get("read_only")){
        return "<i class='fas fa fa-lock' style='padding-right: 4px;' title='" + __("Read only") + "'></i>" + displayValue;
      }
      return "<i class='fas fa fa-pencil' style='padding-right: 4px;'></i>" + displayValue; 
    }

    
    var result, statConf = allStatusConf[status],
      tickPosition = this.whichRange(value, record.get("thresholds"));
    
    if(value){
      result = `<div class='noc-pconf-value fa fa-${statConf.glyph}'`
        + ` style='color:${statConf.color}'>&nbsp;${value}</div>`;
    } else{
      result = `<div class='noc-pconf-value'</div>`;
    }
    result += "<div class='noc-metric-container' style='padding-top:2px;'>";
    if(value){
      result += "<div class='noc-metric-range noc-metric-green-range'></div>";
    }
    if(!Ext.isEmpty(status) && status !== "u"){
      var rangeColors = [
          allStatusConf["c"].color,
          allStatusConf["w"].color,
          allStatusConf["o"].color,
          allStatusConf["w"].color,
          allStatusConf["c"].color,
        ],
        ranges = this.zip([0, 20, 40, 60, 80], rangeColors),
        thresholds = record.get("thresholds"),
        tips = [` < ${thresholds[0]}`,
                `${thresholds[0]} - ${thresholds[1]}`,
                `${thresholds[1]} - ${thresholds[2]}`,
                `${thresholds[2]} - ${thresholds[3]}`,
                `${thresholds[3]} >`];
      
      Ext.each(ranges, function(range, index){
        result += `<div class='noc-metric-range' data-qtip='${tips[index]}'`
          + `style='left:${range[0]}%;width:20%;background: ${range[1]};'></div>`;
      });
    }
    result += "</div>";
    if(value){
      result += `<div class='noc-pconf-value-tick' style='left: calc(${tickPosition}% - 4px);background: ${statConf.color}'></div>`;
    }
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
      return 70;
    } else{
      return 90;
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
