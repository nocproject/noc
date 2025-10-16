//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.core.filter.FilterController");
Ext.define("NOC.core.filter.FilterController", {
  extend: "Ext.app.ViewController",
  alias: "controller.core.filter",

  lookupFields: function(){
    var items = [];

    Ext.Array.each(this.view.items.items, function(item){
      if(item.isLookupField){
        items.push(item);
      }
    });
    return items;
  },

  restoreFilter: function(){
    var queryStr = Ext.util.History.getToken().split("?")[1];
    var parentXtype = this.view.selectionStore.split(".")[0];
    var selectionStoreName = this.view.selectionStore.split(".")[1];
    var view = this.getView().findParentByType(parentXtype);
    //
    if(view){
      var selectionStore = view.getViewModel().getStore(selectionStoreName);
      //
      if(queryStr){
        var params = Ext.Object.fromQueryString(queryStr, true);
        //
        this.view.viewModel.set("filterObject", params);
        if(Object.hasOwn(params, "fav_status")){
          this.view.down("[itemId=fav_status]").setValue(params["fav_status"]);
        }
        Ext.Array.each(this.lookupFields(), function(item){
          var self = this;
          var filterObject = self.view.viewModel.get("filterObject");
          var keys = Object.keys(filterObject);

          keys.filter(function(e){
            return Ext.String.startsWith(e, item.itemId, true);
          }).map(function(e){
            if("caps" === item.itemId){
              var delimiter = filterObject[e].indexOf(":");
              var condition;
              var id, value;
              var typeInclude = true;
              var typeExclude = false;

              if(delimiter >= 0){
                id = filterObject[e].substring(0, delimiter);
                value = filterObject[e].substring(delimiter + 1);

                if(value[0] === "~"){
                  condition = "<";
                  value = value.substring(1);
                } else if(value[value.length - 1] === "~"){
                  condition = ">";
                  value = value.substring(0, value.length - 1);
                } else{
                  condition = "==";
                }
              } else if(filterObject[e][0] === "!"){
                id = filterObject[e].substring(1);
                typeInclude = false;
                typeExclude = true;
              } else{
                id = filterObject[e];
                typeInclude = false;
                typeExclude = false;
              }

              var exist = self.view.viewModel.get("capabilityStore").getNodeById(id);

              if(exist){
                exist.set("typeInclude", typeInclude);
                exist.set("typeExclude", typeExclude);
                exist.set("condition", condition);
                exist.set("value", value);
                exist.set("checked", true);
              }
            } else{
              item.setValue(filterObject[item.itemId]);
            }
          });
        }, this);

        selectionStore.setFilterParams(this.view.viewModel.get("filterObject"));
        this.view.expand();
      }
      selectionStore.load();
    }
  },

  setFilter: function(field, event){
    var value = field.getValue();

    if(field.itemId && "addresses" === field.itemId){
      value = value.split("\n")
                .filter(function(ip){
                  return ip.length > 0;
                })
                .map(function(ip){
                  return ip.trim();
                });

      if(value.length > 2000){
        NOC.msg.failed(__("Too many IP, max 2000"));
        return;
      }
    }

    if("Ext.event.Event" === Ext.getClassName(event)){
      if(Ext.EventObject.ENTER === event.getKey()){
        this.reloadData(field.itemId, value);
      }
      return;
    }

    this.reloadData(field.itemId, value);
  },

  cleanAllFilters: function(){
    Ext.History.add(this.view.appId);
    this.view.viewModel.set("filterObject", {});
    this.onCleanFavorite();
    Ext.Array.each(this.lookupFields(), function(item){
      if("caps" === item.itemId){
        // skip
      } else{
        item.setValue("");
      }
    });
    this.view.viewModel.set("ips", "");
    this.onCapabilitiesClear();
    this.reload();
  },

  cleanFilter: function(field){
    var fieldName = field;

    if(Ext.isObject(field) && "itemId" in field){
      field.setValue("");
      fieldName = field.itemId;
    }
    this.reloadData(fieldName, "");
  },

  reloadData: function(name, value){
    var filterObject = this.view.viewModel.get("filterObject");
    if((typeof value === "string" && value.length > 0)
            || (typeof value === "number")
            || (value !== null && typeof value === "object")){
      if(value === filterObject[name]) return;
      filterObject[name] = value;
    } else{
      if(Object.hasOwn(filterObject, name)){
        delete filterObject[name];
      } else return;
    }

    // don't save addresses into url
    var queryObject = Ext.clone(filterObject);
    if(Object.hasOwn(queryObject, "addresses")){
      delete queryObject["addresses"];
    }

    var token = "", query = Ext.Object.toQueryString(queryObject, true);

    if(query.length > 0){
      token = "?" + query;
    }

    Ext.History.add(this.view.appId + token, true);
    this.reload();
  },

  reload: function(){
    var parentXtype = this.view.selectionStore.split(".")[0];
    var selectionStoreName = this.view.selectionStore.split(".")[1];
    var selectionStore = this.view.findParentByType(parentXtype).viewModel.getStore(selectionStoreName);

    selectionStore.setFilterParams(this.view.viewModel.get("filterObject"));
    selectionStore.load();
  },

  updateCapsFromUrl: function(params){
    var filterObject = this.view.viewModel.get("filterObject");
    var queryObject = filterObject;
    var token = "";
    var keys = Object.keys(queryObject);

    keys.map(function(element){
      if(Ext.String.startsWith(element, "caps")){
        delete filterObject[element];
      }
    }, this);

    var query = Ext.Object.toQueryString(
      Ext.Object.merge(queryObject, params),
      true);

    if(query.length > 0){
      token = "?" + query;
    }

    Ext.History.add(this.view.appId + token, true);
    this.reload();
  },

  onCapabilitiesApply: function(){
    var index = 0;
    var params = {};

    this.view.viewModel.get("capabilityStore").root.cascadeBy(function(element){
      if(element.get("leaf") && element.get("checked")){
        var type = element.get("type");
        var condition = element.get("condition");
        var value;

        if(element.get("typeInclude")){
          if("str" === type){
            value = element.get("id") + ":" + element.get("value");
          } else if("int" === type){
            if("<" === condition){
              value = element.get("id") + ":~" + element.get("value");
            } else if(">" === condition){
              value = element.get("id") + ":" + element.get("value") + "~";
            } else{
              value = element.get("id") + ":" + element.get("value");
            }
          } else if("bool" === type){
            var val = element.get("value");

            if(!val.length) val = false;
            value = element.get("id") + ":" + val;
          }
        } else if(element.get("typeExclude")){
          value = "!" + element.get("id")
        } else{
          value = element.get("id");
        }
        params["caps" + index] = value;
        index++;
      }
    }, this);
    this.updateCapsFromUrl(params);
  },

  onCapabilitiesClear: function(){
    this.view.viewModel.get("capabilityStore").root.cascadeBy(function(element){
      if(element.get("leaf")){
        element.set("checked", false);
      }
    });
    this.updateCapsFromUrl({});
  },

  viewCapValue: function(type, value){
    if("bool" === type){
      this.view.down("#capValueBool").setHidden(!value);
    } else if("int" === type){
      this.view.down("#capCondition").setHidden(!value);
      this.view.down("#capValue").setHidden(!value);
    } else if("str" === type){
      this.view.down("#capValue").setHidden(!value);
    }
  },

  hideAllCaps: function(){
    this.view.down("#capCondition").setHidden(true);
    this.view.down("#capValue").setHidden(true);
    this.view.down("#capValueBool").setHidden(true);
  },

  onChangeCapRecord: function(self, record, operation, modifiedFieldNames){
    var value;
    //
    if(record){
      if(modifiedFieldNames.indexOf("checked") !== -1){
        value = record.get("checked");

        if(!value){
          if(record.get("typeExclude")) record.set("typeExclude", false);
          if(record.get("typeInclude")) record.set("typeInclude", false);
        }
      }
      if(modifiedFieldNames.indexOf("typeInclude") !== -1){
        value = record.get("typeInclude");

        if(value){
          record.set("typeExclude", false);
          if(!record.get("checked")) record.set("checked", true);
          this.viewCapValue(record.get("type"), true);
        } else{
          if(!record.get("typeExclude")){
            if(record.get("checked")) record.set("checked", false);
            this.hideAllCaps();
          }
        }
      }
      if(modifiedFieldNames.indexOf("typeExclude") !== -1){
        value = record.get("typeExclude");

        if(value){
          record.set("typeInclude", false);
          if(!record.get("checked")) record.set("checked", true);
          this.hideAllCaps();
        } else{
          if(!record.get("typeInclude")){
            if(record.get("checked")) record.set("checked", false);
            this.hideAllCaps();
          }
        }
      }
    }
  },

  onCleanFavorite: function(){
    var field = this.view.down("[itemId=fav_status]")
    if(field){
      field.setValue(undefined);
    }
  },

  onChange: Ext.emptyFn,
});