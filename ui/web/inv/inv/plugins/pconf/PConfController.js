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
  mixins: [
    "NOC.inv.inv.plugins.Mixins",
  ],

  onDataChanged: function(store){
    var vm = this.getViewModel();
    if(vm){
      vm.set("totalCount", store.getCount());
    }
  },
  onReload: function(){
    var me = this,
      vm = me.getViewModel(),
      currentId = vm.get("currentId");
    if(Ext.isEmpty(currentId)) return;
    var isUpdatable = this.getView().down("combo[itemId=tabType]").getValue() === 2;
    vm.set("icon", this.generateIcon(isUpdatable, "spinner", "grey", __("loading")));
    Ext.Ajax.request({
      url: "/inv/inv/" + currentId + "/plugin/pconf/data/",
      method: "GET",
      scope: me,
      params: {
        t: vm.get("tabType"),
        g: vm.get("groupParam"),
      },
      success: function(response){
        var data = Ext.decode(response.responseText),
          gridStore = vm.getStore("gridStore");
        gridStore.loadData(data.conf);
        vm.set("icon", this.generateIcon(isUpdatable, "circle", NOC.colors.yes, __("online")));
      },
      failure: function(){
        vm.set("icon", this.generateIcon(isUpdatable, "circle", NOC.colors.no, __("offline")));
        NOC.error(__("Failed to load data"));
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
      method: "POST",
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
  onTabTypeChange: function(combo, record){
    var view = this.getView(),
      getTimerInterval = function(record){
        if(!Ext.isEmpty(record)){
          var interval = record.get("autoreload");
          return interval ? interval * 1000 : undefined;
        }
        return undefined;
      },
      timerInterval = getTimerInterval(record);
    if(Ext.isEmpty(view.getViewModel().get("currentId"))) return;
    this.onReload();
    if(!Ext.isEmpty(timerInterval)){
      if(Ext.isEmpty(view.observer)){
        view.observer = new IntersectionObserver(function(entries){
          view.isIntersecting = entries[0].isIntersecting;
        }, {
          threshold: 1.0,
        });
      }
      view.observer.observe(view.getEl().dom);
      view.timer = Ext.TaskManager.start({
        run: function(){
          var panel = this.getView(),
            vm = this.getViewModel(),
            isVisible = !document.hidden,
            isFocused = document.hasFocus(),
            isIntersecting = panel.isIntersecting,
            isUpdatable = this.getView().down("combo[itemId=tabType]").getValue() === 2;
          if(isIntersecting && isVisible && isFocused){
            vm.set("icon", this.generateIcon(isUpdatable, "circle", NOC.colors.yes, __("online")));
            this.onReload();
          } else{
            vm.set("icon", this.generateIcon(isUpdatable, "stop-circle-o", "grey", __("suspend")));
          }
        },
        interval: timerInterval,
        scope: this,
      });
    } else{
      if(view.timer){
        Ext.TaskManager.stop(view.timer);
        view.timer = null;
      }
      view.getViewModel().set("icon", "<i class='fa fa-fw' style='padding-left:4px;width:16px;'></i>");
    }
  },
  // onButtonsRender: function(segmented){
  //   Ext.each(segmented.getRefItems(), function(button){
  //     var config = this.getView().getStatus()[button.value];
  //     button.setGlyph("x" + NOC.glyph[config.glyph].toString(16));
  //     button.getEl().down(".x-btn-glyph").setStyle("color", config.color);
  //   }, this);
  // },
  onActivate: function(){
    var combo = this.getView().down("combo[itemId=tabType]");
    this.onTabTypeChange(combo, combo.getStore().getById(combo.getValue()));
  },
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
  onMgmtClick: function(){
    var vm = this.getViewModel(),
      url = vm.get("mgmt_url");
    if(Ext.isEmpty(url)) return;
    window.open(url, "_blank");
  },
  // onGroupParamChange: function(){
  // console.log("onGroupParamChange");
  // this.removeFilter();
  // },
});
