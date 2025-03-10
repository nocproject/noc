//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.sa.managedobject.Controller");
Ext.define("NOC.sa.managedobject.Controller", {
  extend: "Ext.app.ViewController",
  requires: [
    "Ext.ux.grid.column.GlyphAction",
  ],
  mixins: [
    "NOC.core.mixins.Export",
  ],
  alias: "controller.managedobject",
  url: "/sa/managedobject/",

  init: function(app){
    var action = this.getView().noc.cmd;
    if(action && action.args && action.args.length >= 1){
      this.editManagedObject(undefined, action.args[0], action.args[1]);
    }
    app.setActiveItem(0);
    app.lookupReference("filterPanel").appId = "sa.managedobject";
    this.restoreSearchField();
  },
  //
  onAddObject: function(grid, rowIndex){
    var checkedRecord = grid.store.getAt(rowIndex);

    grid.getSelectionModel().select(
      grid.getSelectionModel()
                .getSelection()
                .concat(checkedRecord),
    );
    this.getStore("selectedStore").add(checkedRecord);
    // this.viewModel.notify();
  },
  //
  onRemoveObject: function(grid, rowIndex){
    grid.store.removeAt(rowIndex);
  },
  //
  onSelectedStoreSizeChange: function(store){
    this.getViewModel().set("total.selected", this.getStore("selectedStore").getCount());
  },
  //
  onSelectionStoreSizeChange: function(store){
    this.getViewModel().set("total.all", store.getCount());
  },
  //
  collapseFilter: function(){
    this.lookupReference("filterPanel").toggleCollapse();
  },
  //
  toggleBasket: function(){
    this.lookupReference("saManagedobjectSelectedGrid1").toggleCollapse();
  },
  //
  setRowClass: function(grid){
    grid.getView().getRowClass = this.getRowClass;
  },
  //
  getRowClass: function(record){
    var value = record.get("row_class");

    if(value){
      return value;
    }
    return "";
  },
  //
  setStatusClass: function(grid){
    grid.getView().getRowClass = this.getStatusClass;
  },
  //
  getStatusClass: function(record){
    var value = record.get("status");

    if(value){
      var stateCls = {
        w: "noc-status-waiting",
        r: "noc-status-running",
        s: "noc-status-success",
        f: "noc-status-failed",
      };
      var className = stateCls[value];

      if(className){
        return className;
      }
    }
    return "";
  },
  //
  onSelectionRefresh: function(){
    this.lookupReference("saManagedobjectSelectionGrid").getStore().reload();
  },
  //
  onSelectionChange: function(element, selected){
    this.getViewModel().set("total.selection", selected.length);
  },
  //
  onSelectionDblClick: function(grid, record, item, rowIndex){
    if(this.lookupReference("saManagedobjectSelectedGrid1").getCollapsed() === false){
      this.onAddObject(grid, rowIndex);
    } else{
      this.editManagedObject(grid.up("[itemId=sa-managedobject]"), record.id);
    }
  },
  //
  onSelectionSelectAll: function(combo, record){
    var selectionGrid, renderPlugin;

    switch(record.get("cmd")){
      case "SCREEN": {
        selectionGrid = this.lookupReference("saManagedobjectSelectionGrid");
        renderPlugin = selectionGrid.findPlugin("bufferedrenderer");
        selectionGrid.getSelectionModel().selectRange(0, renderPlugin.getLastVisibleRowIndex());
        this.lookupReference("saManagedobjectSelectedGrid1").getStore().loadData(
          this.lookupReference("saManagedobjectSelectionGrid").getSelection(),
        );
        return;
      }
      case "N_ROWS": {
        Ext.Msg.prompt(__("Select rows"), __("Please enter number:"), function(btn, text){
          if(btn === "ok"){
            this.getNRows("0", text);
          }
        }, this);
        break;
      }
      case "PERIOD": {
        Ext.Msg.prompt(__("Select period"), __("Please enter period (start,qty), first pos is 0:"), function(btn, text){
          if(btn === "ok"){
            this.getNRows(text.split(",")[0], text.split(",")[1]);
          }
        }, this);
        break;
      }
      default: {
        this.getNRows("0", record.get("cmd").slice(6));
      }
    }
    combo.setValue(null);
  },
  //
  onSelectionUnselectAll: function(){
    this.lookupReference("saManagedobjectSelectionGrid").getSelectionModel().deselectAll();
  },
  //
  onSelectionAddChecked: function(){
    this.lookupReference("saManagedobjectSelectedGrid1").getStore().add(
      this.lookupReference("saManagedobjectSelectionGrid").getSelection(),
    );
    this.lookupReference("saManagedobjectSelectionGrid").getSelectionModel().deselectAll();
    this.getViewModel().set("total.selected", this.getStore("selectedStore").getCount());
  },
  //
  onSelectedRemoveChecked: function(){
    var selectedGrid = this.lookupReference("saManagedobjectSelectedGrid1");

    selectedGrid.getStore().remove(
      selectedGrid.getSelectionModel().getSelection(),
    );
  },
  //
  onSelectedRemoveAll: function(){
    this.lookupReference("saManagedobjectSelectedGrid1").getStore().removeAll();
  },
  //
  onSelectedDblClick: function(grid, record, item, rowIndex){
    this.lookupReference("saManagedobjectSelectedGrid1").getStore().removeAt(rowIndex);
  },
  //
  onConfigModeChange: function(field, mode){
    var commandForm = this.lookupReference("saManagedobjectCommandForm");

    commandForm.removeAll();
    switch(mode){
      case "action": {
        commandForm.add({
          xclass: "NOC.sa.action.LookupField",
          reference: "saManagedobjectActionField",
          name: "modeId",
          fieldLabel: __("Actions"),
          allowBlank: false,
          editable: false,
          listeners: {
            change: "onChangeAction",
          },
        });
        break;
      }
      case "snippet": {
        commandForm.add({
          xclass: "NOC.sa.commandsnippet.LookupField",
          reference: "saManagedobjectFnippetField",
          name: "modeId",
          fieldLabel: __("Snippets"),
          allowBlank: false,
          editable: false,
          listeners: {
            change: "onChangeSnippet",
          },
        });
        break;
      }
      case "commands": {
        commandForm.add({
          xtype: "textareafield",
          reference: "saManagedobjectCommandField",
          name: "cmd",
          fieldLabel: __("Commands"),
          labelAlign: "top",
          allowBlank: false,
          height: 500,
          scrollable: true,
        });
      }
    }
  },
  //
  onChangeAction: function(field, newValue){
    this.addFields("action", newValue);
  },
  //
  onChangeSnippet: function(field, newValue){
    this.addFields("snippet", newValue);
  },
  //
  onRun: function(){
    var me = this;
    var mode = this.lookupReference("saManagedobjectMode").getValue();
    var makeRequest = function(mode){
      var objects = [];
      var config = me.lookupReference("saManagedobjectCommandForm").getValues();
      var ignore_cli_errors = JSON.stringify(me.lookupReference("ignoreCliErrors").getValue());

      me.getStore("selectedStore").each(function(record){
        objects.push(record.get("id"));
      });

      delete config["modeId"];

      for(var key in config){
        if(config.hasOwnProperty(key)){
          if(!config[key]){
            delete config[key];
          }
        }
      }
      Ext.Ajax.request({
        method: "POST",
        params: JSON.stringify({objects: objects, config: config}),
        headers: {"Content-Type": "application/json"},
        url: Ext.String.format("/sa/runcommands/render/{0}/{1}/", mode, me.idForRender),

        success: function(response){
          var obj = Ext.decode(response.responseText);
          var commands = [];

          for(var key in obj){
            if(obj.hasOwnProperty(key) && obj[key]){
              commands.push({
                id: key,
                script: "commands",
                args: {
                  commands: obj[key].split("\n"),
                  include_commands: true,
                  ignore_cli_errors: ignore_cli_errors,
                },
              });
            }
          }
          if(commands.length > 0){
            me.sendCommands(mode, commands);
          } else{
            NOC.error(__("Empty command"))
          }
        },
        failure: function(response){
          NOC.error(__("server-side failure with status code " + response.status));
        },
      });
    };

    // Reset state
    this.lookupReference("saManagedobjectSelectedGrid3").getSelectionModel().deselectAll();
    this.getViewModel().set("resultOutput", "");

    switch(mode){
      case "commands": {
        this.sendCommands("commands", {
          "script": "commands",
          "args": {
            "commands": this.lookupReference("saManagedobjectCommandForm").getValues().cmd.split("\n"),
            "include_commands": "true",
            "ignore_cli_errors": JSON.stringify(this.lookupReference("ignoreCliErrors").getValue()),
          },
        });
        break;
      }
      default:
        makeRequest(mode);
    }
  },
  //
  onStatusToggle: function(value){
    this.getStore("selectedStore").filterBy(function(record){
      return value.getValue().indexOf(record.get("status")) !== -1;
    });
  },
  //
  onReportClick: function(){
    this.lookupReference("saRunCommandReportPanel").setHtml(this.buildReport());
    this.toNext();
  },
  //
  onShowResult: function(grid, record){
    var acc = [];

    if(record.get("result")){
      this.makeReportRow(record, acc);
    }
    this.getViewModel().set("resultOutput", acc.join("\n"));
  },
  //
  toNext: function(){
    this.navigate(1);
  },
  //
  toPrev: function(){
    this.navigate(-1);
  },
  //
  toMain: function(){
    this.navigate(0, true);
  },
  //
  // Private function
  //
  navigate: function(inc, absolute){
    var l = this.getView().getLayout();
    var i = l.activeItem.activeItem;
    var activeItem = parseInt(i, 10);
    var activate = activeItem + inc;

    if(absolute){
      activate = inc;
    }
    l.setActiveItem(activate);
  },
  //
  addFields: function(mode, newValue){
    var me = this;

    if(newValue){
      this.idForRender = newValue;
      Ext.Ajax.request({
        url: Ext.String.format("/sa/runcommands/form/{0}/{1}/", mode, newValue),

        success: function(response){
          var obj = Ext.decode(response.responseText);
          var commandForm = me.lookupReference("saManagedobjectCommandForm");

          Ext.Array.each(commandForm.items.items.slice(), function(item){
            if(!item.reference){
              commandForm.remove(item);
            }
          });
          // commandForm.removeAll();
          commandForm.add(obj);
        },
        failure: function(response){
          NOC.error(__("server-side failure with status code " + response.status));
        },
      });
    }
  },
  //
  stateInc: function(state, step){
    this.getViewModel().set(state, this.getViewModel().get(state) + step)
  },
  //
  sendCommands: function(mode, cfg){
    var me = this,
      xhr,
      params = [],
      offset = 0,
      rxChunk = /^(\d+)\|/,
      viewModel = this.getViewModel(),
      selectedStore = this.getStore("selectedStore");

    viewModel.set("progressState.r", 0);
    viewModel.set("progressState.w", 0);
    viewModel.set("progressState.f", 0);
    viewModel.set("progressState.s", 0);
    selectedStore.each(function(record){
      var v = {
        id: record.get("id"),
      };


      if("commands" === mode){
        // Copy config
        Ext.Object.each(cfg, function(key, value){
          if(key !== "id"){
            v[key] = value;
          }
        });
        params.push(v);
      } else{
        var param = cfg.filter(function(e){
          return e.id === v.id
        });

        if(param.length){
          params.push(param[0]);
        }
      }
      record.set("status", "w");
    });
    this.toNext();
    viewModel.set("isRunning", true);
    viewModel.set("progressState.w", selectedStore.count());
    // Start streaming request
    xhr = new XMLHttpRequest();
    xhr.open(
      "POST",
      "/api/mrt/",
      true,
    );
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onprogress = function(){
      // Parse incoming chunks
      var ft = xhr.responseText.substr(offset),
        match, l, lh, chunk, record;

      while(ft){
        match = ft.match(rxChunk);
        if(!match){
          break;
        }
        lh = match[0].length;
        l = parseInt(match[1]);
        chunk = JSON.parse(ft.substr(lh, l));
        offset += lh + l;
        ft = ft.substr(lh + l);
        // Process chunk
        record = selectedStore.getById(chunk.id);
        if(chunk.error && "f" !== record.get("status")){
          record.set({
            status: "f",
            result: chunk.error,
          });
          me.stateInc("progressState.r", -1);
          me.stateInc("progressState.f", 1);
        }
        if(chunk.running && "r" !== record.get("status")){
          record.set("status", "r");
          me.stateInc("progressState.w", -1);
          me.stateInc("progressState.r", 1);
        }
        if(chunk.result && "s" !== record.get("status")){
          record.set({
            status: "s",
            result: chunk.result,
          });
          me.stateInc("progressState.r", -1);
          me.stateInc("progressState.s", 1);
        }
      }
    };
    xhr.onload = function(){
      viewModel.set("isRunning", false);
    };
    xhr.onerror = function(e){
      NOC.error("Error!");
      selectedStore.each(function(record){
        if("r" === record.get("status")){
          record.set({
            status: "f",
            result: "RPC call failed: net::ERR_INCOMPLETE_CHUNKED_ENCODING",
          });
          me.stateInc("progressState.r", -1);
          me.stateInc("progressState.f", 1);
        }
      });
      viewModel.set("progressState.r", 0);
      viewModel.set("isRunning", false);
    };
    xhr.send(JSON.stringify(params));
  },
  //
  buildReport: function(){
    var r = [];

    this.getStore("selectedStore").each(function(record){
      if(record.get("result")){
        this.makeReportRow(record, r);
      }
    }, this);
    return r.join("\n");
  },
  //
  makeReportRow: function(record, ac){
    var result = record.get("result");
    var text = "<b>#</b> " + result + "<br/>";

    if(Ext.isFunction(result.map)){
      text = result.map(function(e){
        return "<b>#</b> " + e;
      }).join("<br/>");
    }
    ac.push("<div class='noc-mrt-section'>" + record.get("name") + "(" + record.get("address") + ")</div>");
    ac.push("<div class='noc-mrt-result'>" + text + "</div>");
  },
  //
  getNRows: function(m, n){
    var params, me = this,
      selectionGrid = this.lookupReference("saManagedobjectSelectionGrid"),
      limit = Number.parseInt(n),
      start = Number.parseInt(m);
    if(Number.isInteger(limit) && Number.isInteger(start)){
      params = Ext.Object.merge(
        {},
        Ext.clone(this.lookupReference("saManagedobjectSelectionGrid").getStore().filterParams),
        {
          __limit: limit,
          __start: start,
        },
      );

      selectionGrid.mask(__("Loading"));
      Ext.Ajax.request({
        url: this.lookupReference("saManagedobjectSelectionGrid").getStore().rest_url,
        method: "POST",
        jsonData: params,
        scope: me,
        success: function(response){
          var params = Ext.decode(response.request.requestOptions.data);
          selectionGrid.unmask();
          selectionGrid.getSelectionModel().selectRange(params.__start, params.__start + params.__limit - 1);
          me.lookupReference("saManagedobjectSelectedGrid1").getStore()
                        .insert(0, Ext.decode(response.responseText));
        },
        failure: function(){
          selectionGrid.unmask();
          NOC.error(__("Failed to get data"));
        },
      });

    }
  },
  //
  onDownload: function(){
    var text = $($.parseHTML(this.lookupReference("saRunCommandReportPanel").html)).text(),
      blob = new Blob([text], {type: "text/plain;charset=utf-8"});
    saveAs(blob, "result.txt");
  },
  onGroupEdit: function(){
    var selectedModels = this.lookupReference("saManagedobjectSelectedGrid1").getStore().getData().items,
      selectedIds = Ext.Array.map(selectedModels, function(record){return record.id}),
      formPanel = this.getView().down("[itemId=managedobject-form-panel]"),
      form = formPanel.getForm(),
      disabledFields = Ext.Array.filter(form.getFields().items, function(field){return !field.groupEdit}),
      groupEditFields = Ext.Array.filter(form.getFields().items, function(field){return field.groupEdit}),
      parentCmp = this.lookupReference("saManagedobjectSelectedGrid1").up();
    Ext.Array.each(disabledFields, function(field){field.setDisabled(true)});
    this.view.down("[itemId=formTitle]").update(Ext.String.format(
      formPanel.up().groupChangeTitle, selectedIds.length, formPanel.up("[itemId=sa-managedobject]").appTitle,
    ));
    this.displayButtons(["closeBtn", "groupSaveBtn"]);
    formPanel.ids = selectedIds;
    this.clearForm(form);
    parentCmp.mask(__("Loading"));
    Ext.Ajax.request({
      url: this.url + "full/",
      method: "POST",
      scope: this,
      jsonData: {
        id__in: selectedIds,
      },
      success: function(response){
        var selection = Ext.decode(response.responseText),
          isSameValue = function(data, name){
            var i, isSameValue = true, initValue = data[0][name];
            for(i = 0; i < selection.length; i++){
              if(selection[i][name] !== initValue){
                isSameValue = false;
                break;
              }
            }
            return isSameValue;
          },
          isLookup = function(object, name){
            return Ext.Array.contains(Ext.Object.getKeys(object), name + "__label");
          };
        parentCmp.unmask();
        this.getView().getLayout().setActiveItem("managedobject-form");
        Ext.Array.each(groupEditFields, function(field){
          var value = selection[0][field.name];
          if(selection[0].hasOwnProperty(field.name)){
            if(isSameValue(selection, field.name)){
              if(isLookup(selection[0], field.name)){
                value = {[field.displayField]: selection[0][field.name + "__label"], [field.valueField]: selection[0][field.name]};
              }
            } else{
              value = "Leave unchanged";
            }
            field.setValue(value);
            field.initValue();
          }
        }, this);
        if(this.getView().noc.hasOwnProperty("protected_field")){
          this.setProtectedField(this.getView().noc.protected_field);
        }
      },
      failure: function(){
        parentCmp.unmask();
        NOC.error(__("Failed get group MO detail"));
      },
    });
  },
  onRunDiscovery: function(){
    this.runAction("run_discovery");
  },
  onSetManaged: function(){
    this.runAction("set_managed");
  },
  onSetUnmanaged: function(){
    this.runAction("set_unmanaged");
  },
  onNewMaintenance: function(){
    var basketStore = this.lookupReference("saManagedobjectSelectedGrid1").getStore(),
      objects = Ext.Array.map(basketStore.getData().items, function(record){return {object: record.id, object__label: record.get("name")}}),
      args = {
        direct_objects: objects,
        subject: __("created from managed objects list at ") + Ext.Date.format(new Date(), "d.m.Y H:i P"),
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
  onAddToMaintenance: function(){
    var basketStore = this.lookupReference("saManagedobjectSelectedGrid1").getStore();
    NOC.run(
      "NOC.inv.map.Maintenance",
      __("Add To Maintenance"),
      {
        args: [
          {mode: "Object"},
          Ext.Array.map(basketStore.getData().items, function(record){return {object: record.id, object__label: record.get("name")}}),
        ],
      },
    );
  },
  onEdit: function(gridView, rowIndex, colIndex, item, e, record){
    this.editManagedObject(gridView.up("[itemId=sa-managedobject]"), record.id);
  },
  onFavItem: function(gridView, rowIndex, colIndex, item, e, record){
    var action = record.get("fav_status") ? "reset" : "set",
      url = "/sa/managedobject/favorites/item/" + record.id + "/" + action + "/";

    Ext.Ajax.request({
      url: url,
      method: "POST",
      success: function(){
        // Invert current status
        record.set("fav_status", !record.get("fav_status"));
        gridView.refresh();
      },
    });
  },
  //
  onNewRecord: function(){
    var view = this.getView(),
      formPanel = view.down("[itemId=managedobject-form-panel]");
    formPanel.up().getController().onNewRecord();
    formPanel.up().form = formPanel.getForm();
    view.getLayout().setActiveItem("managedobject-form");
  },
  editManagedObject: function(gridView, id, suffix, isEmbedded){
    var url = this.url + id + "/",
      view = this.getView();

    if(gridView){
      gridView.mask(__("Loading"));
    }
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: this,
      success: function(response){
        if(response.status === 200){
          var field,
            formPanel,
            form,
            formView,
            standardMode = ["closeBtn", "saveBtn", "resetBtn", "deleteBtn", "createBtn", "cloneBtn", "showMapBtn",
                            "configBtn", "confDBBtn", "cardBtn", "dashboardBtn", "consoleBtn", "scriptsBtn", "interfacesBtn",
                            "sensorsBtn", "linksBtn", "discoverBtn", "alarmsBtn", "inventoryBtn", "cmdBtn", "helpBtn"],
            embeddedMode = ["saveBtn", "showMapBtn", "configBtn", "confDBBtn", "cardBtn", "dashboardBtn",
                            "consoleBtn", "scriptsBtn", "interfacesBtn", "sensorsBtn", "linksBtn", "discoverBtn",
                            "alarmsBtn", "inventoryBtn", "cmdBtn", "helpBtn"],
            r = {},
            data = Ext.decode(response.responseText),
            record = Ext.create("NOC.sa.managedobject.Model", data);

          if(!gridView){ // restore by url
            gridView = this.getView();
          }
          record.set("id", id);
          formPanel = gridView.down("[itemId=managedobject-form-panel]");
          formView = formPanel.up();
          formPanel.recordId = id;
          formPanel.currentRecord = record;
          form = formPanel.getForm();
          Ext.Array.each(form.getFields().items, function(field){
            var isDisabled = Ext.Array.contains(["is_managed"], field.name);
            field.setDisabled(isDisabled);
          });
          Ext.iterate(data, function(v){
            if(v.indexOf("__") !== -1){
              return
            }
            field = form.findField(v);
            if(!field){
              return;
            }
            // hack to get instance of .TreeCombo class
            if(Ext.String.endsWith(field.xtype, ".TreeCombo")){
              field[0].restoreById(data[v]);
              return;
            }
            if(Ext.isFunction(field.cleanValue)){
              var rest_url = field.restUrl ? field.restUrl : field.store.rest_url,
                value = {[v]: data[v], [v + "__label"]: data[v + "__label"], id: data.id},
                record = Ext.create("Ext.data.Model", value);

              r[v] = field.cleanValue(record, rest_url);
              return;
            }
            r[v] = data[v];
          });
          //
          this.getView().down("[itemId=managedobject-form]").down().form = form;
          this.clearForm(form);
          form.setValues(r);
          this.loadInlineStore(formPanel, data.id);
          if(isEmbedded === undefined){
            view.setHistoryHash(data.id);
          }
          this.dirtyReset(form);
          view.getLayout().setActiveItem("managedobject-form").down().setActiveItem("managedobject-form-panel");
          this.displayButtons(isEmbedded === undefined ? standardMode : embeddedMode);
          if(suffix){
            formView.getController().itemPreview("sa-" + suffix);
          }
          this.setFormTitle(formView.changeTitle, data);
          this.showMapHandler(record);
        }
        if(view.noc.hasOwnProperty("protected_field")){
          this.setProtectedField(view.noc.protected_field);
        }
        if(gridView && isEmbedded === undefined){
          gridView.unmask();
        }
      },
      failure: function(){
        if(gridView){
          gridView.unmask();
        }
        NOC.error(__("Failed get MO detail"));
      },
    });
  },
  // reset dirty flag
  dirtyReset: function(form){
    Ext.each(form.getFields().items, function(field){
      if(Ext.isFunction(field.resetOriginalValue)){
        field.resetOriginalValue();
      }
    });
  },
  // Set edit form title
  setFormTitle: function(tpl, data){
    var t = "<b>" + Ext.String.format(tpl, this.view.appTitle) + "</b>",
      formTitle = this.view.down("[itemId=formTitle]"),
      itemId = data.id;
    if(itemId !== "NEW" && itemId !== "CLONE"){
      itemId = "<b>ID:</b>" + itemId + NOC.clipboardIcon(itemId);
    } else{
      itemId = "<b>" + itemId + "</b>";
    }
    t += "<span style='float:right'>" + itemId + "</span>";
    if(data.is_wiping){
      t += "<br/><span style='float:left'>" + __("Device is wiping and will be removed soon") + "</span>";
    }
    formTitle.update(t);
  },
  resetInlineStore: function(formPanel, defaults){
    Ext.each(formPanel.query("[itemId$=-inline]"),
             function(gridField){
               var store, value = [];
               store = new Ext.create("NOC.core.InlineModelStore", {
                 model: gridField.model,
               });
               gridField.setStore(store);
               if(store.hasOwnProperty("rootProperty") && this.hasOwnProperty(store.rootProperty)){
                 value = this[store.rootProperty];
               }
               store.loadData(value);
             }, defaults || {});
  },
  loadInlineStore(formPanel, id){
    Ext.each(formPanel.query("[itemId$=-inline]"),
             function(gridField){
               var store = new Ext.create("NOC.core.InlineModelStore", {
                 model: gridField.model,
               });
               gridField.setStore(store);
               store.setParent(id);
               store.load();
             }, this);
  },
  showMapHandler: function(record){
    Ext.Ajax.request({
      url: "/sa/managedobject/" + record.get("id") + "/map_lookup/",
      method: "GET",
      scope: this,
      success: function(response){
        var me = this, menuItems,
          showMapBtn = this.getView().down("[itemId=showMapBtn]"),
          data = Ext.decode(response.responseText);

        showMapBtn.setHandler(function(){
          showMapBtn.showMenu();
        }, me);
        showMapBtn.getMenu().removeAll();
        menuItems = data.filter(function(el){
          return !el.is_default
        }).map(function(el){
          return {
            text: el.label,
            handler: function(){
              NOC.launch("inv.map", "history", {
                args: el.args,
              })
            },
          }
        });
        Ext.Array.each(menuItems, function(item){
          showMapBtn.getMenu().add(item);
        });
      },
      failure: function(){
        NOC.error(__("Show Map Button : Failed to get data"));
      },
    });
  },
  onCellClick: function(self, td, cellIndex, record, tr, rowIndex, e){
    var cellName = e.position.column.dataIndex;
    if(["interface_count", "link_count"].includes(cellName)){
      this.editManagedObject(undefined, record.id, cellName);
    }
  },
  displayButtons(displayItems){
    var formButtons = this.getView().down("[itemId=managedobject-form]").down().getDockedItems()[0].getRefItems();
    Ext.Array.each(formButtons, function(button){
      button.setVisible(Ext.Array.contains(displayItems, button.itemId));
    })
  },
  runAction: function(actionName){
    var me = this,
      basketStore = this.lookupReference("saManagedobjectSelectedGrid1").getStore(),
      ids = Ext.Array.map(basketStore.getData().items, function(record){return record.id});
    Ext.Ajax.request({
      url: "/sa/managedobject/" + "actions/" + actionName + "/",
      method: "POST",
      scope: me,
      jsonData: {ids: ids},
      success: function(response){
        this.reloadSelectionGrids();
        NOC.info(Ext.decode(response.responseText) || "OK");
      },
      failure: function(){
        NOC.error(__("Action") + " " + actionName + " " + __("failed"));
      },
    });
  },
  reloadSelectionGrids: function(){
    var mainGrid = this.getView().down("[reference=saManagedobjectSelectionGrid]"),
      basketGrid = this.getView().down("[reference=saManagedobjectSelectedGrid1]"),
      ids = Ext.Array.map(basketGrid.getStore().getData().items, function(record){return record.id});
    mainGrid.mask(__("Loading"));
    mainGrid.getStore().reload({
      callback: function(){
        mainGrid.unmask();
      },
    });
    if(ids.length > 0){
      basketGrid.mask(__("Loading"));
      Ext.Ajax.request({
        url: this.url + "full/",
        method: "POST",
        scope: this,
        jsonData: {
          id__in: ids,
        },
        success: function(response){
          var data = Ext.decode(response.responseText);
          basketGrid.unmask();
          basketGrid.getStore().loadData(data);
        },
        failure: function(){
          basketGrid.unmask();
          NOC.error(__("Failed refresh basket"));
        },
      });
    }
  },
  onExportBasket: function(){
    var date = "_" + Ext.Date.format(new Date(), "YmdHis"),
      filename = this.getView().appId.replace(/\./g, "_") + date + ".csv";
    this.save(this.lookupReference("saManagedobjectSelectedGrid1"), filename);
  },
  cleanSearchField: function(field){
    field.setValue(null);
    this.lookupReference("filterPanel").getController().setFilter(field);
  },
  onSearchFieldChange: function(field){
    this.lookupReference("filterPanel").getController().setFilter(field);
  },
  restoreSearchField: function(){
    var param = "__query",
      queryStr = Ext.util.History.getToken().split("?")[1];
    if(queryStr && queryStr.includes(param)){
      var query = Ext.Object.fromQueryString(queryStr, true);
      this.getView().down("[itemId=" + param + "]").setValue(query[param]);
    }
  },
  setProtectedField(fields){
    Ext.Object.each(fields, function(fieldName, value){
      var field = this.getView().down("[name=" + fieldName + "]");

      switch(value){
        case 0:
          field.setHidden(true);
          break;
        case 1:
        case 2:
          field.setDisabled(true);
          break;
      }
    }, this);
  },
  clearForm: function(form){
    Ext.each(form.getFields().items, function(field){
      field.setValue(null);
    });
  },
  saveFilterToUrl: function(filter){
    var params = Ext.Object.toQueryString(filter, true)
      , currentHash = Ext.History.getHash()
      , index = currentHash.indexOf("?")
      , app;
    if(index === -1){
      app = currentHash;
    } else{
      app = currentHash.substr(0, index);
    }
    if(params){
      Ext.History.add(app + "?" + params);
    } else{
      Ext.History.add(app);
    }
  },
});
