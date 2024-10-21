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
    this.uuidGenerator = new Ext.data.identifier.Uuid();
    this.templates = {
      loading: __("Loading {0} plugin, please wait..."),
      fetching: __("Fetching data for {0}..."),
      processing: __("Processing {0} items..."),
      reloading: __("Reloading {0} ..."),
    };
        
    this.handleMaskTimeout = this.handleMaskTimeout.bind(this);
  },

  handleMaskTimeout: function(messageId){
    if(!this.maskedComponent) return;
        
    var message = Ext.Array.findBy(this.activeMessages, function(msg){
      return msg.id === messageId;
    });
    if(message){
      message.timeout = null;
      this.maskedComponent.mask(this.getLastMessage());
    }
  },

  show: function(templateKeyOrMessage, args){
    var self = this;
    var id = this.uuidGenerator.generate();
    var message = this.templates[templateKeyOrMessage] || templateKeyOrMessage;
    var formattedMessage = Ext.String.format.apply(Ext.String, [message].concat(args || []));
        
    if(this.activeMessages.length > 100){
      var oldestMessage = this.activeMessages[0];
      if(oldestMessage && oldestMessage.timeout){
        clearTimeout(oldestMessage.timeout);
      }
      this.activeMessages.shift();
    }
        
    var timeout = setTimeout(function(){
      self.handleMaskTimeout(id);
    }, 500);
        
    this.activeMessages.push({
      id: id, 
      message: formattedMessage,
      timeout: timeout,
    });

    return id;
  },

  hide: function(id){
    var message = Ext.Array.findBy(this.activeMessages, function(msg){
      return msg.id === id;
    });
        
    if(message && message.timeout){
      clearTimeout(message.timeout);
    }

    Ext.Array.remove(this.activeMessages, message);

    if(this.activeMessages.length === 0){
      if(this.maskedComponent){
        this.maskedComponent.unmask();
      }
    } else if(this.maskedComponent){
      this.maskedComponent.mask(this.getLastMessage());
    }
  },

  getLastMessage: function(){
    return this.activeMessages.length > 0 ? 
      this.activeMessages[this.activeMessages.length - 1].message : 
      null;
  },

  destroy: function(){
    Ext.Array.each(this.activeMessages, function(message){
      if(message.timeout){
        clearTimeout(message.timeout);
      }
    });
        
    this.activeMessages = null;
    this.maskedComponent = null;
    this.uuidGenerator = null;
    this.templates = null;
    this.handleMaskTimeout = null;
        
    this.callParent(arguments);
  },
});
