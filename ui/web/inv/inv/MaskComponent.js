//---------------------------------------------------------------------
// inv.inv Mask Component for inv.inv application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.MaskComponent");

Ext.define("NOC.inv.inv.MaskComponent", {
  extend: "Ext.Component",
  constructor: function(config){
    this.callParent(arguments);
    this.maskedComponent = config.maskedComponent;
    this.activeMessages = [];
    this.maskTimeout = null;
    this.uuidGenerator = new Ext.data.identifier.Uuid();
    this.templates = {
      loading: __("Loading {0} plugin, please wait..."),
      fetching: __("Fetching data for {0}..."),
      processing: __("Processing {0} items..."),
    };
  },

  show: function(templateKeyOrMessage, args){
    var id = this.uuidGenerator.generate();
    var message;

    if(this.templates[templateKeyOrMessage]){
      message = this.templates[templateKeyOrMessage];
    } else{
      message = templateKeyOrMessage;
    }

    var formattedMessage = Ext.String.format.apply(Ext.String, [message].concat(args || []));
    this.activeMessages.push({id: id, message: formattedMessage});

    if(!this.maskTimeout){
      this.maskTimeout = setTimeout(function(){
        this.maskedComponent.mask(this.getLastMessage());
        this.maskTimeout = null;
      }.bind(this), 500);
    } else{
      this.maskedComponent.mask(this.getLastMessage());
    }

    return id;
  },

  hide: function(id){
    this.activeMessages = this.activeMessages.filter(function(msg){
      return msg.id !== id;
    });

    if(this.activeMessages.length === 0){
      clearTimeout(this.maskTimeout);
      this.maskTimeout = null;
      this.maskedComponent.unmask();
    } else{
      this.maskedComponent.mask(this.getLastMessage());
    }
  },

  getLastMessage: function(){
    return this.activeMessages.length > 0 ? this.activeMessages[this.activeMessages.length - 1].message : null;
  },
});