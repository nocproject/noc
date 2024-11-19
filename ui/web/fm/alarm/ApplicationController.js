//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.ApplicationController");

Ext.define("NOC.fm.alarm.ApplicationController", {
  extend: "Ext.app.ViewController",
  alias: "controller.fm.alarm",
  activeFiltersInitValues: {
    status: "A",
    collapse: 1,
    maintenance: "hide",
    alarm_group: "show",
    ephemeral: 0,
    wait_tt: 0,
    managed_object: "",
    segment: "",
    administrative_domain: "",
    resource_group: "",
    alarm_class: "",
    escalation_tt__contains: "",
    timestamp__gte: null,
    timestamp__lte: null,
    profiles: [],
    fav_status: null,
  },
  recentFiltersInitValues: {
    status: "C",
    collapse: 1,
    cleared_after: 0,
  },
  activeBinding: undefined,
  recentBinding: undefined,
  displayBinding: undefined,
  init: function(view){
    var url = Ext.History.getHash().split("?"),
      viewModel = view.getViewModel(),
      prefix = url[0], queryStr = url.length ? url[1] : undefined;
    this.initFilter(viewModel);
    if(this.getView().getCmd() === "history" && Object.prototype.hasOwnProperty.call(this.getView().noc, "cmd")){
      var alarmId = this.getView().noc.cmd.args[0];
      if(this.urlHasId("fm.alarm/" + alarmId)){
        view.setHistoryHash(alarmId);
        this.openForm();
      }
    } else if(this.urlHasId(prefix)){
      view.setHistoryHash(prefix.split("/")[1]);
      this.openForm();
    } else{
      if(url[0] === "fm.alarm"){
        if(queryStr && queryStr !== "__format=ext&status=A&alarm_group=show&maintenance=hide&collapse=1&ephemeral=0&cleared_after=0"){
          this.deserialize(queryStr, viewModel);
        } else{ // restore from local store
          var filter = window.localStorage.getItem("fm-alarm-filter");
          if(filter){
            this.deserialize(filter, viewModel);
          }
        }
      }
    }
    this.activeBinding = viewModel.bind({
      bindTo: "{activeFilter}",
      deep: true,
    }, this.onChangeActiveFilters, this);
    this.recentBinding = viewModel.bind({
      bindTo: "{recentFilter.cleared_after}",
    }, this.onChangeRecentParams, this);
    this.displayBinding = viewModel.bind({
      bindTo: "{displayFilter}",
      deep: true,
    }, this.onChangeDisplayFilters, this);
    this.callParent();
  },
  initFilter: function(viewModel){
    var hasProfiles, duration;
    viewModel.set("activeFilter", Ext.clone(this.activeFiltersInitValues));
    viewModel.set("recentFilter", Ext.clone(this.recentFiltersInitValues));
    hasProfiles = this.readLocalStore("fm-alarm-has-profiles");
    duration = this.readLocalStore("fm-alarm-duration");
    if(hasProfiles){
      viewModel.set("displayFilter.hasProfiles", hasProfiles);
    }
    if(duration){
      viewModel.set("displayFilter.duration", duration);
    }
  },
  destroy: function(){
    this.activeBinding.destroy();
    this.recentBinding.destroy();
    this.displayBinding.destroy();
  },
  onChangeActiveFilters: function(data){
    var listsView = this.getView().lookupReference("fm-alarm-list"),
      grid = listsView.lookupReference("fm-alarm-active"),
      store = grid.getStore(),
      filter = this.serialize(data);
    grid.mask(__("Loading..."));
    store.getProxy().setExtraParams(filter);
    store.load({
      params: filter,
      callback: function(){
        grid.unmask();
      },
    });
    this.activeSelectionFiltered(data);
    this.updateHash(false);
  },
  onChangeRecentParams: function(data){
    var listsView = this.getView().lookupReference("fm-alarm-list"),
      filter = this.getViewModel().get("recentFilter"),
      panel = listsView.lookupReference("fm-alarm-recent"),
      store = panel.getStore();
    // don't change, http params is string compare with int,  1 == "1"
    panel.setHidden(data == 0);
    panel.mask(__("Loading..."));
    store.getProxy().setExtraParams(filter);
    store.load({
      params: filter,
      callback: function(){
        panel.unmask();
      },
    });
    this.updateHash(false);
  },
  onChangeDisplayFilters: function(data){
    if(Object.prototype.hasOwnProperty.call(data, "hasProfiles") && !Ext.Object.isEmpty(data.hasProfiles)){
      window.localStorage.setItem("fm-alarm-has-profiles", JSON.stringify(data.hasProfiles));
    } else{
      this.getViewModel().set("displayFilter.hasProfiles",
                              this.getView().down("[itemId=fm-alarm-multi-panel]").getInitValues());
    }
    if(Object.prototype.hasOwnProperty.call(data, "duration") && !Ext.Object.isEmpty(data.duration)){
      window.localStorage.setItem("fm-alarm-duration", JSON.stringify(data.duration));
    } else{
      this.getViewModel().set("displayFilter.duration",
                              this.getView().down("[itemId=fm-alarm-duration-filter]").getInitValues());
    }
    this.reloadActiveGrid();
  },
  onOpenForm: function(form, record){
    this.openForm(record.id);
  },
  onCloseForm: function(){
    this.reloadActiveGrid();
    this.getViewModel().set("activeItem", "fm-alarm-list");
    this.updateHash(true);
  },
  onResetFilter: function(){
    this.initFilter(this.getViewModel());
  },
  onRefreshForm: function(){
    var id = this.getViewModel().get("selected.id");
    this.getAlarmDetail(id);
  },
  // private
  deserialize: function(queryStr, viewModel){
    var params, cleared_after, listsView, profiles,
      setParam = function(name, value){
        if(!Object.prototype.hasOwnProperty.call(params, name)){
          params[name] = value;
        }
      },
      restoreCombo = function(name){
        var me = this;
        if(Object.prototype.hasOwnProperty.call(params, name)){
          var store = me.getView().down("[name=" + name + "]").getStore();
          store.load({
            params: {id: params[name]}, callback: function(records){
              if(records && records.length > 0){
                viewModel.set("activeFilter." + name, records[0]);
              }
            },
          });
          delete params[name];
        }
      },
      restoreTagField = function(name){
        var me = this, acc = [], filter = {},
          // resultMock = [],
          keys = Object.keys(params),
          length = keys.length;
        for(var i = 0; i < length; i++){
          var key = keys[i];
          if(Ext.String.startsWith(key, name)){
            acc.push(params[key]);
            filter["id" + i + "__in"] = params[key];
            // resultMock.push(Ext.create("Ext.data.Model", {
            //     id: params[key],
            //     label: key
            // }));
            delete params[key];
          }
        }
        if(acc.length){
          // viewModel.set("activeFilter." + name, resultMock);
          var store = me.getView().down("[name=" + name + "]").getStore();
          store.load({
            params: filter, callback: function(records){
              if(records && records.length > 0){
                viewModel.set("activeFilter." + name, records);
              }
            },
          });
        }
      },
      makeProfile = function(){
        var profileKeys, len, i, acc = [];
        profileKeys = Ext.Object.getKeys(params);
        len = profileKeys.length;
        for(i = 0; i < len; i++){
          var key = profileKeys[i];
          if(Ext.String.startsWith(key, "profile")){
            var profile = {};
            // if(profile) {
            var tokens = params[key].split(":");
            profile.profileId = tokens[0];
            profile.condition = "gt";
            if(Ext.String.startsWith(tokens[1], "~")){
              profile.condition = "lt";
            }
            profile.value = tokens[1].replace("~", "");
            acc.push(profile);
            delete params[key];
          }
        }
        return acc;
      };
    params = Ext.Object.fromQueryString(queryStr, true);
    delete params["__format"];
    // default params
    setParam("collapse", 0);
    setParam("wait_tt", 0);
    // restore date and datetime params
    Ext.each(["timestamp__gte", "timestamp__lte"], function(name){
      if(Object.prototype.hasOwnProperty.call(params, name)){
        params[name] = Ext.Date.parse(params[name], "Y-m-d\\TH:i:s");
      }
    });
    // restore field which use selection binding
    Ext.each([
      "managed_object",
      "resource_group",
      "segment",
    ], restoreCombo, this);
    // restore tag fields
    Ext.each([
      "alarm_class",
      "administrative_domain",
    ], restoreTagField, this);
    // don't change, http params is string compare with int, 0 == "0"
    if(Object.prototype.hasOwnProperty.call(params, "cleared_after") && params.cleared_after != 0){
      listsView = this.getView().lookupReference("fm-alarm-list");
      cleared_after = params["cleared_after"];
      listsView.lookupReference("fm-alarm-sidebar").down("[reference=fm-alarm-recent-switcher]").setExpanded(true);
    } else{
      cleared_after = 0;
    }
    delete params["cleared_after"];
    // restore profile widget
    profiles = makeProfile();
    if(profiles.length > 0){
      params["profiles"] = Ext.Array.sort(profiles, function(item1, item2){
        return item1.index < item2.index ? -1 : 1
      });
    }
    viewModel.set("activeFilter", params);
    viewModel.set("recentFilter.cleared_after", cleared_after);
  },
  serialize: function(value){
    var filter = {"__format": "ext"},
      setParam = function(param){
        if(Ext.isEmpty(value[param.key])){
          return;
        }
        if(param.defaultValue){
          // don't change, http params is string compare with int, 1 == "1"
          if(value[param.key] == param.defaultValue){
            filter[param.key] = param.defaultValue;
          }
        } else if(param.valueField){
          if(Ext.isArray(value[param.key])){
            if(value[param.key].length === 1){
              filter[param.key] = value[param.key][0][param.valueField];
            } else{
              // filter[param.key + "__in"] = value[param.key].join(",");
              Ext.Array.map(value[param.key], function(element, index){
                filter[param.key + index + "__in"] = element[param.valueField];
              })
            }
          } else{ // if use selection in binding
            filter[param.key] = value[param.key][param.valueField];
          }
        } else{
          filter[param.key] = value[param.key];
        }
      };
    Ext.each([
      {key: "status"},
      {key: "maintenance"},
      {key: "alarm_group"},
      {key: "fav_status"},
      {key: "collapse", defaultValue: 1},
      {key: "ephemeral", defaultValue: 0},
      {key: "wait_tt", defaultValue: 1},
      // search field
      {key: "escalation_tt__contains"},
      // datetime
      {key: "timestamp__gte"},
      {key: "timestamp__lte"},
      // tree
      {key: "segment", valueField: "id"},
      // combo
      {key: "managed_object", valueField: "id"},
      {key: "resource_group", valueField: "id"},
      // tag field
      {key: "alarm_class", valueField: "id"},
      {key: "administrative_domain", valueField: "id"},
    ], setParam);
    if(Object.prototype.hasOwnProperty.call(value, "profiles")){
      var i, len = value.profiles.length;
      for(i = 0; i < len; i++){
        var item = value.profiles[i], v = item.profileId + ":",
          // key = (item.type === "SRV" ? "service_profile" : "subscribers_profile") + i;
          key = "profile" + i;
        if(item.condition === "gt"){
          v += item.value + "~";
        } else if(item.condition === "lt"){
          v += "~" + item.value;
        }
        filter[key] = v;
      }
    }
    return filter;
  },
  updateHash: function(force){
    if(force || !this.urlHasId(Ext.History.getHash())){
      var queryStr = Ext.merge(
        this.serialize(this.getViewModel().get("activeFilter")),
        {
          cleared_after: this.getViewModel().get("recentFilter.cleared_after"),
        });
      this.setHash(queryStr);
      window.localStorage.setItem("fm-alarm-filter", Ext.Object.toQueryString(queryStr, true));
    }
  },
  setUrl: function(id){
    var prefix = Ext.History.getHash().split(/[/?]/)[0];
    Ext.History.setHash(prefix + "/" + id);
  },
  setHash: function(val){
    var prefix = Ext.History.getHash().split(/[/?]/)[0];
    Ext.History.setHash(prefix + "?" + Ext.Object.toQueryString(val, true));
  },
  urlHasId: function(url){
    var tokens = url.split("/"),
      isId = function(str){
        return /^[0-9a-f]{24}$/i.test(str);
      };
    if(tokens.length === 1){
      return false;
    }
    if(tokens[0] !== "fm.alarm"){
      return false;
    }
    return !!(tokens.length > 1 && isId(tokens[1]));
  },
  openForm: function(id){
    this.getViewModel().set("activeItem", "fm-alarm-form");
    if(id){
      this.setUrl(id);
    } else{ // restore from url
      id = Ext.History.getHash().split(/[/?]/)[1];
    }
    this.getView().down("[reference=fm-alarm-form-tab-panel]").setActiveTab(0);
    this.getAlarmDetail(id);
  },
  getAlarmDetail: function(alarmId){
    Ext.Ajax.request({
      url: "/fm/alarm/" + alarmId + "/",
      method: "GET",
      scope: this,
      success: function(response){
        this.getViewModel().set("selected", Ext.decode(response.responseText));
      },
      failure: function(){
        NOC.error(__("Failed to get alarm"));
      },
    });
  },
  readLocalStore: function(name){
    var data = window.localStorage.getItem(name);
    return JSON.parse(data);
  },
  reloadActiveGrid: function(){
    var panel = this.getView().down("[reference=fm-alarm-active]"),
      activeStore = panel.getStore();

    panel.mask(__("Loading..."));
    activeStore.reload({
      callback: function(){
        panel.unmask();
      },
    });
  },
  activeSelectionFiltered: function(filter){
    var grid = this.getView().down("[reference=fm-alarm-active]");

    if(grid.getSelection().length > 0){
      this.selectionFilter(grid.getSelection(), filter);
    }
  },
  selectionFilter: function(data, filter){
    if(!filter){
      filter = this.getViewModel().get("activeFilter");
    }
    Ext.Ajax.request({
      url: "/fm/alarm/",
      method: "POST",
      scope: this,
      jsonData: Ext.merge({
        id__in: Ext.Array.map(data, function(item){
          return item.id;
        }),
      }, this.serialize(filter)),
      success: function(response){
        var selectionSummary, summary, selection,
          selectionFiltered = Ext.decode(response.responseText),
          alarmListModel = this.lookup("fm-alarm-list").getViewModel(),
          selected = alarmListModel.get("total.selectionFiltered");

        if(selectionFiltered.length){
          selection = Ext.Array.flatten(Ext.Array.map(selectionFiltered, function(item){
            return item.total_subscribers.concat(item.total_services)
          }));
          selectionSummary = Ext.Array.reduce(selection, function(prev, item){
            if(Object.prototype.hasOwnProperty.call(prev, item.profile)){
              prev[item.profile] += item.summary
            } else{
              prev[item.profile] = item.summary
            }
            return prev;
          }, {});

          summary = Ext.Array.map(selected, function(item){
            return Ext.merge(item, {
              summary: (Object.prototype.hasOwnProperty.call(selectionSummary, item.id)) ? selectionSummary[item.id] : 0,
            });
          });
        } else{
          summary = Ext.Array.map(selected, function(item){
            return Ext.merge(item, {summary: 0});
          });
        }
        alarmListModel.set("total.selectionFiltered", summary);
        alarmListModel.set("total.objectsFiltered", Ext.Array.reduce(selectionFiltered, function(prev, item){
          return prev + item.total_objects;
        }, 0));
      },
      failure: function(){
        var message = "Error";
        NOC.error(message)
      },
    });
  },
});
