//---------------------------------------------------------------------
// ip.ipam.prefix form
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.prefix.PrefixAddressListsController");

Ext.define("NOC.ip.ipam.view.forms.prefix.PrefixAddressListsController", {
  extend: "Ext.app.ViewController",
  alias: "controller.ip.ipam.list.prefixAddress",
  onShowFreePrefixes: function(button){
    this.showFree(button, "prefix", this.filterByFree);
  },
  onShowFreeAddresses: function(button){
    this.showFree(button, "address", this.filterByFree);
  },
  onViewPrefixContents: function(view, record, item, idx, evt){
    if(evt.getTarget(".prefix-bookmark")){
      Ext.Ajax.request({
        url: "/ip/ipam/" + record.id + "/toggle_bookmark/",
        method: "GET",
        success: function(response){
          var result = Ext.decode(response.responseText);
          record.set("has_bookmark", result.has_bookmark);
        },
      });
    } else if(evt.getTarget(".prefix-view")){
      if(record.get("isFree")){
        this.fireViewEvent("ipIPAMPrefixFormNew", {prefix: record.get("name")});
      } else{
        this.fireViewEvent("ipIPAMViewPrefixContents", {id: record.id});
      }
    } else if(evt.getTarget(".prefix-edit")){
      this.fireViewEvent("ipIPAMPrefixFormEdit", {id: record.id});
    }
  },
  onViewAddresses: function(view, record, item, idx, evt){
    if(evt.getTarget(".address-view")){
      if(record.get("isFree")){
        this.fireViewEvent("ipIPAMAddressFormNew", {address: record.get("address")});
      } else{
        this.fireViewEvent("ipIPAMAddressFormEdit", {id: record.id});
      }
    }
  },
  onVRFListOpen: function(){
    this.fireViewEvent("ipIPAMVRFListOpen");
  },
  onNavigationClick: function(event, el){
    var id, pattern = /nav-\d+/,
      cls = el.className.match(pattern);
    if(!Ext.isEmpty(cls)){
      id = cls[0].replace("nav-", "");
      this.fireViewEvent("ipIPAMViewPrefixContents", {id: id});
    } else{
      console.error(el.className + " not match '" + pattern + "'");
    }
  },
  onSelectBookmark: function(combo, record){
    this.fireViewEvent("ipIPAMViewPrefixContents", {id: record.id});
  },
  onQuickJump: function(field, key){
    if(key.getKey() === Ext.EventObject.ENTER){
      var vrf_id = this.getViewModel().get("prefix.vrf"),
        afi = this.getViewModel().get("prefix.afi");
      Ext.Ajax.request({
        url: "/ip/ipam/" + vrf_id + "/" + afi + "/quickjump/",
        method: "POST",
        scope: this,
        jsonData: {
          jump: field.getValue(),
        },
        success: function(response){
          var result = Ext.decode(response.responseText);
          this.fireViewEvent("ipIPAMViewPrefixContents", {id: result.id});
        },
        failure: function(r){
          var msg = r.responseText || r.statusText;
          NOC.error(msg);
        },
      });
    }
  },
  showFree: function(button, name, filter){
    var store = this.getView().down("[itemId=ipam-" + name + "-grid]").getStore();
    if(store.isFiltered()){
      store.clearFilter();
      button.setText(__("Hide Free") + " " + __(Ext.String.capitalize(name)));
    } else{
      store.addFilter(filter);
      button.setText(__("Show Free") + " " + __(Ext.String.capitalize(name)));
    }
  },
  filterByFree: function(record){
    return !record.data.isFree;
  },
});
