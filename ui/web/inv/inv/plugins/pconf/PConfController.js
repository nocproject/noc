//---------------------------------------------------------------------
// inv.inv PConf Controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.pconf.PConfController");

Ext.define("NOC.inv.inv.plugins.pconf.PConfController", {
  extend: "Ext.app.ViewController",
  alias: "controller.pconf",

  onDataChanged: function(store){
    var vm = this.getViewModel();
    if(vm){
      vm.set("totalCount", store.getCount());
    }
  },
  onReload: function(){
    var me = this,
      currentId = me.getViewModel().get("currentId"),
      panel = me.getView(),
      maskComponent = panel.up("[appId=inv.inv]").maskComponent,
      messageId = maskComponent.show("fetching", "pconf");
    Ext.Ajax.request({
      url: "/inv/inv/" + currentId + "/plugin/pconf/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText),
          vm = me.getViewModel(),
          group = vm.get("groupParam");
        panel.preview(data);
        vm.set("groupParam", group);
      },
      failure: function(){
        NOC.error(__("Failed to load data"));
      },
      callback: function(){
        maskComponent.hide(messageId);
      },
    });
  },
  onValueChanged: function(data){
    var me = this,
      maskComponent = me.getView().up("[appId=inv.inv]").maskComponent,
      messageId = maskComponent.show("saving", "pconf"),
      currentId = me.getViewModel().get("currentId");
    Ext.Ajax.request({
      url: "/inv/inv/" + currentId + "/plugin/pconf/set/",
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
      callback: function(){
        maskComponent.hide(messageId);
      },
    });
  },
  // onStatusChange: function(group, button){
  //   var store = this.getViewModel().getStore("gridStore"),
  //     filters = store.getFilters();
   
  //   this.removeFilter();
  //   if(button.pressed){
  //     filters.add({
  //       id: "invConfigStatusFilter",
  //       filterFn: function(record){
  //         var status = record.get("status");
  //         return button.value === status
  //       },
  //     });
  //   }
  // },
  onTabTypeChange: function(combo){
    var me = this.getView();
    if(combo.getValue() === 2){
      if(Ext.isEmpty(me.observer)){
        me.observer = new IntersectionObserver(function(entries){
          me.isIntersecting = entries[0].isIntersecting;
        }, {
          threshold: 1.0,
        });
      }
      me.observer.observe(me.getEl().dom);
      me.timer = Ext.TaskManager.start({
        run: function(){
          var panel = this.getView(),
            isVisible = !document.hidden,
            isFocused = document.hasFocus(),
            isIntersecting = panel.isIntersecting;
          if(isIntersecting && isVisible && isFocused){
            panel.up("[appId=inv.inv]").maskComponent.hide(panel.messageId);
            panel.messageId = undefined;
            this.onReload();
          } else{
            if(Ext.isEmpty(panel.messageId)){
              panel.messageId = panel.up("[appId=inv.inv]").maskComponent.show("auto reload suspended");
            }
          }
        },
        interval: me.timerInterval,
        scope: this,
      });
    } else{
      if(me.timer){
        Ext.TaskManager.stop(me.timer);
        me.timer = null;
      }
    }
  },
  // onButtonsRender: function(segmented){
  //   Ext.each(segmented.getRefItems(), function(button){
  //     var config = this.getView().getStatus()[button.value];
  //     button.setGlyph("x" + NOC.glyph[config.glyph].toString(16));
  //     button.getEl().down(".x-btn-glyph").setStyle("color", config.color);
  //   }, this);
  // },
  valueRenderer: function(value, metaData, record){
    var displayValue,
      units = record.get("units"),
      allStatusConf = this.getView().getStatus(),
      status = record.get("status");
    if(record.get("type") === "enum"){
      var options = record.get("options") || [],
        option = options.find(opt => opt.id === value);
      displayValue = option ? option.label : value;
    }

    if(Ext.isEmpty(value)){
      displayValue = "";
    } else{
      displayValue = value + "&nbsp;" + units || "";
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
        + ` style='color:${statConf.color}'>&nbsp;${displayValue}</div>`;
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
    return result;
  },
  whichRange: function(value, ranges){
    var val = parseFloat(value),
      position = function(val, index){
        return (val - parseFloat(ranges[index - 1])) * 20 / (parseFloat(ranges[index]) - parseFloat(ranges[index - 1])) + index * 20;
      };
    if(Ext.isEmpty(ranges) || ranges.filter(range => Ext.isEmpty(range)).length > 0){
      return 50;
    }
    if(val < parseFloat(ranges[0])){
      return 10;
    } else if(val < parseFloat(ranges[1])){
      return position(val, 1);
    } else if(val < parseFloat(ranges[2])){
      return position(val, 2);
    } else if(val < parseFloat(ranges[3])){
      return position(val, 3);
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
  // onGroupParamChange: function(){
  // console.log("onGroupParamChange");
  // this.removeFilter();
  // },
});
