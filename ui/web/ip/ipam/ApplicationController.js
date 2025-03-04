//---------------------------------------------------------------------
// ip.ipam application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.ApplicationController");

Ext.define("NOC.ip.ipam.ApplicationController", {
  extend: "Ext.app.ViewController",
  alias: "controller.ip.ipam",
  init: function(view){
    var id, mode, url = Ext.History.getHash().split("?"),
      // viewModel = view.getViewModel(),
      prefix = url[0], queryStr = url.length ? url[1] : undefined;

    if(prefix){
      this.getView().currentHistoryHash = prefix;
    }
    // url router
    if(Ext.String.startsWith(prefix, "ip.ipam/vrf")){
      id = prefix.replace("ip.ipam/vrf", "").replace("/", "");
      mode = id ? "edit" : "new";
      this.openVRFForm(id, mode);
    } else if(Ext.String.startsWith(prefix, "ip.ipam/prefix/delete/")){
      id = prefix.replace("ip.ipam/prefix/delete/", "").replace("/", "");
      this.openPrefixDeleteForm(id);
    } else if(Ext.String.startsWith(prefix, "ip.ipam/prefix/")){
      id = prefix.replace("ip.ipam/prefix/", "").replace("/", "");
      this.openPrefixForm(id, "edit");
    } else if(Ext.String.startsWith(prefix, "ip.ipam/address/")){
      id = prefix.replace("ip.ipam/address/", "").replace("/", "");
      this.openAddressForm(id, "edit");
    } else if(Ext.String.startsWith(prefix, "ip.ipam/")){
      this.openPrefixContents(prefix.replace("ip.ipam/", ""));
    }
    this.callParent();
  },
  onRebaseFormClose: function(){
    var prefixForm = this.getView().down("[itemId=ipam-prefix-form]");
    prefixForm.loadPrefix(this.getViewModel().get("prefix.id"));
    this.getViewModel().set("activeItem", "ipam-prefix-form");
  },
  onPrefixFormEdit: function(view, params){
    var prefixId = params.id || this.getViewModel().get("prefix.id");
    this.openPrefixForm(prefixId, "edit");
  },
  onPrefixFormNew: function(veiw, params){
    var id = this.getViewModel().get("prefix.id");
    this.openPrefixForm(id, "new", params.prefix);
  },
  onPrefixFormClose: function(params){
    this.openPrefixContents("contents/" + params.id + "/");
  },
  onPrefixDeleteFormOpen: function(){
    var id = this.getViewModel().get("prefix.id");
    this.openPrefixDeleteForm(id);
  },
  onPrefixDeleteFormClose: function(params){
    this.openPrefixContents("contents/" + params.id + "/");
  },
  onAddressFormEdit: function(view, params){
    this.openAddressForm(params.id, "edit");
  },
  onAddressFormNew: function(view, params){
    this.openAddressForm(undefined, "new", params.address);
  },
  onAddressFormClose: function(params){
    this.openPrefixContents("contents/" + params.id + "/");
  },
  onVRFFormEdit: function(grid, record){
    this.openVRFForm(record.id, "edit");
  },
  onVRFFormClose: function(){
    this.openVRFList();
  },
  onToolsFormOpen: function(parentForm, param){
    var form = this.getView().down("[itemId=ipam-tools-form]");

    form.getViewModel().set("prefix", param.prefix);
    this.getViewModel().set("activeItem", "ipam-tools-form");
  },
  onToolsFormClose: function(form){
    var prefix = form.getViewModel().get("prefix");
    this.openPrefixContents("contents/" + prefix.id + "/");
  },
  onPrefixContentsOpen: function(grid, params){
    var url = "contents/" + params.id + "/";
    if(params.hasOwnProperty("afi")){
      url = "get_vrf_prefix/" + params.id + "/" + params.afi + "//";
    }
    this.openPrefixContents(url);
  },
  onPrefixContentsClose: function(){
    this.openParentPrefix();
  },
  openAddressForm: function(addressId, mode, address){
    var form = this.getView().down("[itemId=ipam-address-form]");
    this.getViewModel().set("activeItem", "ipam-address-form");
    if(mode === "edit"){
      form.loadAddress(addressId);
      this.setUrl("address/" + addressId + "/");
    } else{
      form.newAddress(this.getViewModel().get("prefix.id"), address);
    }
  },
  openPrefixForm: function(prefixId, mode, prefixName){
    var form = this.getView().down("[itemId=ipam-prefix-form]");
    this.getViewModel().set("activeItem", "ipam-prefix-form");
    if(mode === "edit"){
      form.loadPrefix(prefixId);
      this.setUrl("prefix/" + prefixId + "/");
    } else if(mode === "new"){
      form.newPrefix(prefixId, prefixName);
    }
  },
  openPrefixDeleteForm: function(prefixId){
    var form = this.getView().down("[itemId=ipam-prefix-del-form]");
    this.getViewModel().set("activeItem", "ipam-prefix-del-form");
    this.setUrl("prefix/delete/" + prefixId + "/");
    form.preview(prefixId);
  },
  openVRFForm: function(id, mode){
    this.getViewModel().set("activeItem", "ipam-vrf-form");
    if(mode === "edit"){
      this.loadDetail("/ip/vrf/" + id, "", "vrf");
    }
  },
  openVRFList: function(){
    this.getViewModel().set("activeItem", "ipam-vrf-list");
    this.updateHash(true);
  },
  openPrefixContents: function(hash){
    this.getViewModel().set("activeItem", "ipam-prefix-contents");
    this.loadDetail("/ip/ipam/", hash, "prefix");
  },
  openParentPrefix: function(){
    var parentId, path = this.getViewModel().get("prefix.path");
    if(path != null && path.length > 1){
      parentId = path[path.length - 1].parent_id;
      this.openPrefixContents("contents/" + parentId + "/");
    } else{
      this.openVRFList();
    }
  },
  loadDetail: function(prefix, hash, variable){
    Ext.Ajax.request({
      url: prefix + hash,
      method: "GET",
      scope: this,
      success: function(response){
        var value = Ext.decode(response.responseText);
        if(value.hasOwnProperty("state")){
          value.state = {
            value: value.state,
            label: value.state__label,
            itemId: value.id,
          };
        }
        this.getViewModel().set(variable, value);
        if(Ext.String.endsWith(hash, "//")){ // change vrf_id on prefix_id
          hash = "contents/" + value.id;
        }
        this.setUrl(hash);
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  setUrl: function(hash){
    var prefix;
    if(hash){
      prefix = Ext.History.getHash().split(/[/?]/)[0];
      Ext.History.setHash(prefix + "/" + hash);
    }
  },
  setQuery: function(val){
    var prefix = Ext.History.getHash().split(/[/?]/)[0],
      query = val ? "?" + Ext.Object.toQueryString(val, true) : "";
    Ext.History.setHash(prefix + query);
  },
  updateHash: function(force){
    if(force){
      this.setQuery();
    }
  },
  onChange: Ext.emptyFn,
});
