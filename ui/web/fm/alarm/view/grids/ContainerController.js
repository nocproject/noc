//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.ContainerController");
Ext.define("NOC.fm.alarm.view.grids.ContainerController", {
  extend: "Ext.app.ViewController",
  alias: "controller.fm.alarm.container",
  requires: [
    "NOC.fm.alarm.view.form.ClearAlarms",
  ],
  pollingTaskId: undefined,
  pollingInterval: 120000,
  initViewModel: function(){
    var profiles = Ext.create("NOC.fm.alarm.store.Profile", {autoLoad: false});
    profiles.load({
      scope: this,
      callback: function(records){
        this.getViewModel().set("total.selected", Ext.Array.map(records, function(record){
          return Ext.merge(record.clone().data, {summary: 0});
        }, this));
        this.getViewModel().set("total.selectionFiltered", Ext.Array.map(records, function(record){
          return Ext.merge(record.clone().data, {summary: 0});
        }, this));
      },
    });
  },
  init: function(view){
    this.observer = new IntersectionObserver(function(entries){
      view.isIntersecting = entries[0].isIntersecting;
    }, {
      threshold: 0.1,
    });
    this.callParent();
    this.subscribeToEvents();
  },
  destroy: function(){
    this.unsubscribeFromEvents();
    this.stopPolling();
    this.setContainerDisabled(false);
  },
  subscribeToEvents: function(){
    window.addEventListener("focus", this.handleWindowFocus.bind(this));
    window.addEventListener("blur", this.handleWindowBlur.bind(this));
  },
  unsubscribeFromEvents: function(){
    window.removeEventListener("focus", this.handleWindowFocus.bind(this));
    window.removeEventListener("blur", this.handleWindowBlur.bind(this));
  },
  onSoundToggle: function(self, pressed){
    this.getViewModel().set("volume", pressed);
  },
  onResetFilter: function(){
    this.fireViewEvent("fmAlarmResetFilter");
  },
  handleWindowFocus: function(){
    this.disableHandler(false);
  },
  //
  handleWindowBlur: function(){
    this.disableHandler(true);
  },
  disableHandler: function(state){
    var isVisible = !document.hidden, // check is user has switched to another tab browser
      isIntersecting = this.getView().isIntersecting; // switch to other application tab
    if(this.pollingTaskId && isIntersecting && isVisible){
      this.setContainerDisabled(state);
      this.pollingTask();
    }
  },
  setContainerDisabled: function(value){
    var app = this.getView().up("[itemId=fm-alarm]"),
      vm = app.getViewModel();
    vm.set("containerDisabled", value);
  },
  onAutoReloadToggle: function(self, pressed){
    this.getViewModel().set("autoReload", pressed);
    this.setContainerDisabled(false);
    if(pressed){
      this.startPolling();
    } else{
      this.stopPolling();
    }
  },
  startPolling: function(){
    this.observer.observe(this.getView().getEl().dom);
    if(Ext.isEmpty(this.pollingTaskId)){
      this.pollingTaskId = Ext.TaskManager.start({
        run: this.pollingTask,
        interval: this.pollingInterval,
        scope: this,
      });
    } else{
      this.pollingTask();
    }
  },
  stopPolling: function(){
    if(this.pollingTaskId){
      Ext.TaskManager.stop(this.pollingTaskId);
      this.pollingTaskId = undefined;
    }
  },
  pollingTask: function(){
    var app = this.getView().up("[itemId=fm-alarm]"),
      gridsContainer = this.getView(),
      isVisible = !document.hidden, // check is user has switched to another tab browser
      isFocused = document.hasFocus(), // check is user has minimized browser window
      isIntersecting = this.getView().isIntersecting; // switch to other application tab
    
    // lib visibilityJS
    if(isIntersecting && isVisible && isFocused){ // check is user has switched to another tab or minimized browser window
      this.setContainerDisabled(false);
      // Check for new alarms and play sound
      this.checkNewAlarms();
      // Poll only application tab is visible
      if(!app.ownerCt.isVisible()){ // e.g. app.isActive()
        return;
      }
      // Poll only when in grid preview
      if(!gridsContainer.isVisible()){
        return;
      }
      // Poll only if polling is not locked
      if(this.isNotLocked(gridsContainer)){
        gridsContainer.down("[reference=fm-alarm-active]").getStore().reload();
        if(this.isRecentActive()){
          gridsContainer.down("[reference=fm-alarm-recent]").getStore().reload();
        }
      }
    } else{
      this.setContainerDisabled(true);
    }
  },
  isRecentActive: function(){
    return this.getViewModel().get("recentFilter.cleared_after") > 0
  },
  isNotLocked: function(container){
    var viewTable = container.down("[reference=fm-alarm-active]").getView(),
      buttonPressed = this.getViewModel().get("autoReload"),
      isNotScrolling = viewTable.getScrollable().getPosition().y === 0,
      contextMenuHidden = viewTable.isHidden();
    return buttonPressed && isNotScrolling && contextMenuHidden;
  },
  checkNewAlarms: function(){
    var ts, delta;
    ts = new Date().getTime();
    if(this.lastCheckTS && this.getViewModel().get("volume")){
      delta = Math.ceil((ts - this.lastCheckTS) / 1000.0);
      Ext.Ajax.request({
        url: "/fm/alarm/notification/?delta=" + delta,
        scope: this,
        success: function(response){
          var data = Ext.decode(response.responseText);
          if(data.sound){
            Ext.applyIf(this, {sounds: {} });
            this.sounds[data.sound] = new Audio(data.sound);
            this.sounds[data.sound].volume = data.volume || 1.0;
            this.sounds[data.sound].play();
          }
        },
      });
    }
    this.lastCheckTS = ts;
  },
  onRefresh: function(){
    this.getView().lookup("fm-alarm-active").getStore().reload();
    if(this.isRecentActive()){
      this.getView().lookup("fm-alarm-recent").getStore().reload();
    }
  },
  onReload: function(grid){
    grid.getStore().reload();
  },
  onStoreLoaded: function(self, store){
    this.getViewModel().set("total.alarmsTotal", store.getTotalCount());
  },
  onSelectAlarm: function(grid, record){
    this.fireViewEvent("fmAlarmSelectItem", record);
  },
  onStoreSelectionChange: function(grid){
    var selection = Ext.Array.flatten(Ext.Array.map(grid.getSelection(), function(item){
        return item.get("total_subscribers").concat(item.get("total_services"))
      })),
      selectionSummary = Ext.Array.reduce(selection, function(prev, item){
        if(Object.prototype.hasOwnProperty.call(prev, item.profile)){
          prev[item.profile] += item.summary
        } else{
          prev[item.profile] = item.summary
        }
        return prev;
      }, {}),
      selected = this.getViewModel().get("total.selected");
    this.getView().up("[reference=fm-alarm]").getController().activeSelectionFiltered();
    this.getViewModel().set("total.objects", Ext.Array.reduce(grid.getSelection(), function(prev, item){
      return prev + item.get("total_objects");
    }, 0));
    this.getViewModel().set("total.selected", Ext.Array.map(selected, function(item){
      return Ext.merge(item, {
        summary: (Object.prototype.hasOwnProperty.call(selectionSummary, item.id)) ? selectionSummary[item.id] : 0,
      });
    }));
  },
  //
  generateSummaryHtml: function(records, filter, force){
    var isEmpty = function(array){
        if(!array){
          return true;
        }
        return array.length === 0;
      },
      isEqual = function(item1, item2){
        return item1.id === item2.id;
      },
      intersect = function(array1, array2){
        var intersection = [], i, j, len1, len2;
        if(isEmpty(array1) || isEmpty(array2)){
          return [];
        }
        len1 = array1.length;
        len2 = array2.length;
        for(i = 0; i < len1; i++){
          for(j = 0; j < len2; j++){
            if(isEqual(array1[i], array2[j])){
              intersection.push(array1[i]);
            }
          }
        }
        return intersection;
      },
      contains = function(array, element){
        var i, len = array.length;
        for(i = 0; i < len; i++){
          if(isEqual(element, array[i])){
            return true;
          }
        }
        return false;
      },
      minus = function(array1, array2){
        var acc = [], i, len1;
        if(isEmpty(array1)){
          return [];
        }
        len1 = array1.length;
        for(i = 0; i < len1; i++){
          if(!contains(array2, array1[i])){
            acc.push(array1[i]);
          }
        }
        return acc;
      },
      summaryHtml = function(records){
        var summaryHtml = "",
          summarySpan = "<span class='x-summary'>",
          badgeSpan = "<span class='x-display-tag'>",
          closeSpan = "</span>",
          sortFn = function(a, b){
            if(a.display_order > b.display_order){
              return 1;
            } else{
              return -1;
            }
          },
          iconTag = function(cls, title){
            return "<i class='" + cls + "' title='" + title + "'></i>";
          },
          badgeTag = function(value){
            return badgeSpan + value + closeSpan;
          },
          profileHtml = function(profile){
            return iconTag(profile.icon, profile.label)
                            + badgeTag(profile.summary);
          },
          profilesHtml = function(profiles){
            if(profiles.length){
              summaryHtml += summarySpan;
              summaryHtml += profiles.map(profileHtml).join("");
              summaryHtml += closeSpan;
            }
          };
        profilesHtml(Ext.Array.sort(records, sortFn));
        return summaryHtml;
      };
    if(!Ext.Object.isEmpty(filter)){
      if(filter.include){
        return summaryHtml(intersect(records, filter.array));
      } else{
        return summaryHtml(minus(records, filter.array));
      }
    }
    if(force){
      return summaryHtml(records);
    }
    // use html from backend
    return "";
  },
  addGroupComment: function(){
    var grid = this.lookupReference("fm-alarm-active"),
      ids = grid.getSelection().map(function(alarm){
        return alarm.id
      }),
      view = this.getView(),
      msg = new Ext.window.MessageBox().prompt(
        __("Set group comment"),
        __("Please enter comment"),
        function(btn, text){
          if(btn === "ok"){
            Ext.Ajax.request({
              url: "/fm/alarm/comment/post/",
              method: "POST",
              jsonData: {
                ids: ids,
                msg: text,
              },
              success: function(){
                view.up("[itemId=fm-alarm]").getController().reloadActiveGrid();
                NOC.info(__("Success"));
              },
              failure: function(){
                NOC.error(__("Failed to save group comment"));
              },
            });
          }
        },
        this,
      );
    msg.setWidth(500);
  },
  addGroupEscalate: function(){
    var grid = this.lookupReference("fm-alarm-active"),
      ids = grid.getSelection().map(function(alarm){
        return alarm.id
      });
    Ext.Ajax.request({
      url: "/fm/alarm/escalate/",
      method: "POST",
      jsonData: {
        ids: ids,
      },
      scope: this,
      success: function(response){
        var data = Ext.decode(response.responseText);
        if(data.status){
          NOC.info(__("Escalated"));
        } else{
          NOC.error(__("Escalate failed : ") + (Object.prototype.hasOwnProperty.call(data, "error") ? data.error : "unknowns error!"));
        }
      },
      failure: function(){
        NOC.error(__("Escalate failed"));
      },
    });
  },
  onActiveResetSelection: function(){
    this.lookupReference("fm-alarm-active").setSelection(null);
  },
  createMaintenance: function(){
    var selection = this.lookupReference("fm-alarm-active").getSelection(),
      objects = selection.map(function(alarm){
        return {
          object: alarm.get("managed_object"),
          object__label: alarm.get("managed_object__label"),
        }
      }),
      args = {
        direct_objects: objects,
        subject: __("created from alarms list at ") + Ext.Date.format(new Date(), "d.m.Y H:i P"),
        contacts: NOC.email ? NOC.email : NOC.username,
        start_date: Ext.Date.format(new Date(), "d.m.Y"),
        start_time: Ext.Date.format(new Date(), "H:i"),
        stop_time: "12:00",
        suppress_alarms: true,
      };
    Ext.create("NOC.maintenance.maintenancetype.LookupField")
            .getStore()
            .load({
              params: {__query: "РНР"},
              callback: function(records){
                if(records.length > 0){
                  Ext.apply(args, {
                    type: records[0].id,
                  })
                }
                NOC.launch("maintenance.maintenance", "new", {
                  args: args,
                });
              },
            });
  },
  openAlarmDetailReport: function(){
    var selection = this.lookupReference("fm-alarm-active").getSelection(),
      ids = selection.map(function(alarm){
        return alarm.id
      });
    NOC.launch("fm.reportalarmdetail", "new", {ids: ids});

  },
  collapseFilter: function(){
    this.lookupReference("fm-alarm-sidebar").toggleCollapse();
  },
  onGroupUnmarkFavorites: function(){
    this.groupFavoritesOperation("reset");
  },
  onGroupMarkFavorites: function(){
    this.groupFavoritesOperation("set"); 
  },
  groupFavoritesOperation(action){
    var grid = this.lookupReference("fm-alarm-active"),
      ids = grid.getSelection().map(function(alarm){
        return alarm.id
      });
    Ext.Ajax.request({
      url: "/fm/alarm/group/favorites/",
      method: "POST",
      scope: this,
      jsonData: {
        ids: ids,
        fav_status: action === "set",
      },
      success: function(response){
        var data = Ext.decode(response.responseText);
        if(data.status){
          this.getView().up("[itemId=fm-alarm]").getController().reloadActiveGrid();
          NOC.info(__("Success"));
        } else{
          NOC.error(__("Failed to " + action + " favorites"));
        }
      },
      failure: function(){
        NOC.error(__("Failed to " + action + " favorites"));
      },
    });
  },
  onClearAlarms: function(){
    Ext.create("NOC.fm.alarm.view.form.ClearAlarms", {
      parentController: this.getView().up("[itemId=fm-alarm]").getController(),
      alarms: this.lookupReference("fm-alarm-active").getSelection().map(function(alarm){
        return {
          id: alarm.id,
          managed_object: alarm.get("managed_object"),
          managed_object__label: alarm.get("managed_object__label"),
        }
      }),
    }).show();
  },
});
