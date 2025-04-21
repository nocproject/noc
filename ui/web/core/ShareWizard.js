//---------------------------------------------------------------------
// NOC.core.ShareWizard - wizard for sharing items
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ShareWizard");

Ext.define("NOC.core.ShareWizard", {
  extend: "Ext.window.Window",
  title: __("Share Contribution"),
  modal: true,
  resizable: false,
  width: 650,
  height: 450,
  layout: "fit",
  closeAction: "destroy",
  defaultListenerScope: true,
  restUrl: undefined,
  
  // State machine states
  STATE_START: "start",
  STATE_ENTER_API_KEY: "apiKey",
  STATE_GET_SHARED_INFO: "getSharedInfo",
  STATE_ENTER_DESCRIPTION: "description",
  STATE_FINISH: "finish",
  
  // Components references
  getnocAPIContribURL: "https://api.getnoc.com/api/v1/contrib",
  apiTokenEndpoint: "/main/apitoken/noc-gitlab-api/",
  items: [
    {
      xtype: "panel",
      layout: "card",
      itemId: "cardPanel",
      border: false,
      tbar: [
        {
          itemId: "progressBar",
          xtype: "progressbar",
          width: "100%"},
      ],
      defaults: {
        bodyPadding: 20,
      },
      items: [
        { // STATE_START
          xtype: "panel",
          itemId: "start",
          layout: {
            type: "vbox",
            align: "center",
            pack: "center",
          },
          items: [
            {
              xtype: "container",
              html: "<h2>" + __("Preparing Contribution") + "</h2><p>" + __("Getting API key, please wait...") + "</p>",
            },
            {
              xtype: "container", 
              margin: "20 0 0 0",
              items: [
                {
                  xtype: "progressbar",
                  width: 300,
                  itemId: "startProgress",
                },
              ],
            },
          ],
        },
        { // STATE_ENTER_API_KEY
          xtype: "form",
          itemId: "apiKey",
          layout: {
            type: "vbox",
            align: "stretch",
          },
          items: [
            {
              xtype: "container",
              html: "<h2>" + __("API Key Required") + "</h2><p>" + __("Please enter your GitLab API key to continue.") + "</p>",
              margin: "0 0 20 0",
            },
            {
              xtype: "textfield",
              fieldLabel: __("GitLab API Key"),
              name: "apiKey",
              allowBlank: false,
              labelWidth: 120,
              emptyText: __("Enter your GitLab API key"),
            },
          ],
          buttons: [
            {
              text: __("Cancel"),
              handler: "onCancel",
            },
            {
              text: __("Next"),
              formBind: true,
              handler: "onApiKeySubmit",
            },
          ],
        },
        { // STATE_GET_SHARED_INFO
          xtype: "panel",
          itemId: "getSharedInfo",
          layout: {
            type: "vbox",
            align: "center",
            pack: "center",
          },
          items: [
            {
              xtype: "container",
              html: "<h2>" + __("Getting Information") + "</h2><p>" + __("Retrieving additional information, please wait...") + "</p>",
            },
            {
              xtype: "container", 
              margin: "20 0 0 0",
              items: [
                {
                  xtype: "progressbar",
                  width: 300,
                  itemId: "sharedInfoProgress",
                },
              ],
            },
          ],
        },
        { // STATE_ENTER_DESCRIPTION
          xtype: "form",
          itemId: "description",
          layout: {
            type: "vbox",
            align: "stretch",
          },
          items: [
            {
              xtype: "container",
              html: "<h2>" + __("Contribution Details") + "</h2><p>" + __("Please provide a description for your contribution.") + "</p>",
              margin: "0 0 20 0",
            },
            {
              xtype: "textarea",
              fieldLabel: __("Description"),
              name: "description",
              labelWidth: 120,
              flex: 1,
              emptyText: __("Enter an optional description for your contribution"),
            },
          ],
          buttons: [
            {
              text: __("Modify API Key"),
              handler: "onDescriptionBack",
            },
            {
              text: __("Share"),
              formBind: true,
              handler: "onDescriptionSubmit",
            },
          ],
        },
        { // STATE_FINISH
          xtype: "panel",
          itemId: "finish",
          layout: {
            type: "vbox",
            align: "center",
            pack: "center",
          },
          items: [
            {
              xtype: "container",
              itemId: "finishMessage",
              html: "<h2>" + __("Thank You!") + "</h2><p>" + __("Your contribution has been shared successfully.") + "</p>",
            },
            {
              xtype: "container",
              itemId: "finishError",
              hidden: true,
              html: "<h2>" + __("Error") + "</h2><p>" + __("There was an error sharing your contribution.") + "</p>",
            },
            {
              xtype: "container",
              itemId: "contributionUrl",
              margin: "20 0 0 0",
              hidden: true,
              items: [
                {
                  xtype: "displayfield",
                  fieldLabel: __("Contribution URL"),
                  labelWidth: 120,
                  name: "url",
                  value: "",
                },
                {
                  xtype: "button",
                  text: __("Open in Browser"),
                  margin: "10 0 0 0",
                  handler: "onOpenContribution",
                },
              ],
            },
          ],
          buttons: [
            {
              text: __("Close"),
              handler: "onClose",
            },
          ],
        },
      ],
    },
  ],
  initComponent: function(){
    this.callParent();
    this.progressBar = this.down("#progressBar");
    this.initStateMachine();
  },
  
  // State machine definition
  initStateMachine: function(){
    this.stateMachine = {
      [this.STATE_START]: {
        enter: this.enterStartState,
        transitions: {
          success: this.STATE_GET_SHARED_INFO,
          failure: this.STATE_ENTER_API_KEY,
        },
      },
      [this.STATE_ENTER_API_KEY]: {
        enter: this.enterApiKeyState,
        transitions: {
          success: this.STATE_GET_SHARED_INFO,
          failure: this.STATE_FINISH,
        },
      },
      [this.STATE_GET_SHARED_INFO]: {
        enter: this.getSharedInfoState,
        transitions: {
          success: this.STATE_ENTER_DESCRIPTION,
          failure: this.STATE_FINISH,
        },
      },
      [this.STATE_ENTER_DESCRIPTION]: {
        enter: this.enterDescriptionState,
        transitions: {
          success: this.STATE_FINISH,
          failure: this.STATE_FINISH,
        },
      },
      [this.STATE_FINISH]: {
        enter: this.enterFinishState,
        transitions: {},
      },
    };
    
    this.stateData = {}; // Shared data between states
    this.currentState = null;
  },
  
  // Start the sharing process
  startProcess: function(data){
    this.data = data; // The data to be shared
    this.show();
    
    // Start the state machine
    this.transitionTo(this.STATE_START);
  },
  
  // Transition to a new state
  transitionTo: function(stateName, transitionType){
    var me = this;
    
    if(me.currentState && transitionType){
      var currentState = me.stateMachine[me.currentState];
      if(currentState.transitions[transitionType]){
        stateName = currentState.transitions[transitionType];
      }
    }
    
    me.currentState = stateName;
    
    // Activate the corresponding card
    me.down("#cardPanel").getLayout().setActiveItem(stateName);
    
    console.debug("Transitioning to state: " + stateName);
    // Execute the state's entry function
    var state = me.stateMachine[stateName];
    if(state && typeof state.enter === "function"){
      state.enter.call(me);
    }
  },
  
  // STATE_START implementation
  enterStartState: function(){
    var me = this;
    
    // Update progress
    me.progressBar.updateProgress(0.1, __("Checking API key..."));
    
    // Create animation for the start progress
    var startProgress = me.down("#startProgress"),
      animate = function(){
        if(startProgress.rendered && !startProgress.isDestroyed){
          startProgress.updateProgress(
            Math.min(1, startProgress.getValue() + 0.05),
            null,
            true,
          );
        
          if(startProgress.getValue() < 1){
            Ext.defer(animate, 100);
          }
        }
      };
    
    animate();
    
    // Check for existing API key
    me.getAPIToken().then(
      function(token){
        me.stateData.apiKey = token;
        me.progressBar.updateProgress(0.3, __("API key found"));
        me.down("textfield[name=apiKey]").setValue(token);
        me.transitionTo(null, "success");
      },
      function(){
        // Failure - need to ask for API key
        me.progressBar.updateProgress(0.2, __("API key required"));
        me.transitionTo(null, "failure");
      },
    );
  },
  // STATE_ENTER_API_KEY implementation
  enterApiKeyState: function(){
    var me = this;
    me.progressBar.updateProgress(0.2, __("Waiting for API key..."));
  },
  
  // GET_SHARED_INFO implementation
  getSharedInfoState: function(){
    var me = this;
    me.progressBar.updateProgress(0.4, __("Getting additional information..."));
    
    me.getSharedInfo().then(
      function(info){
        me.stateData.sharedInfo = info;
        me.progressBar.updateProgress(0.5, __("Information received"));
        me.transitionTo(null, "success");
      },
      function(error){
        me.stateData.error = __("Failed to get shared info: ") + error;
        me.progressBar.updateProgress(0.4, __("Error getting information"));
        me.transitionTo(null, "failure");
      },
    );
  },  
  // STATE_ENTER_DESCRIPTION implementation
  enterDescriptionState: function(){
    var me = this;
    me.progressBar.updateProgress(0.5, __("Ready to share..."));
  },
  
  // STATE_FINISH implementation
  enterFinishState: function(){
    var me = this;
    
    // Show success or error message based on stateData
    if(me.stateData.error){
      me.down("#finishMessage").hide();
      me.down("#finishError").show();
      me.down("#finishError").update("<h2>" + __("Error") + "</h2><p>" + me.stateData.error + "</p>");
      me.progressBar.updateProgress(1.0, __("Failed"));
      me.statusBarColor = me.getProgressBarColor();
      me.setProgressBarColor("#e74c3c");
    } else{
      me.down("#finishMessage").show();
      me.down("#finishError").hide();
      me.progressBar.updateProgress(1.0, __("Completed"));
      // Show contribution URL if available
      if(me.stateData.url){
        me.down("#contributionUrl").show();
        me.down("displayfield[name=url]").setValue(me.stateData.url);
      } else{
        me.down("#contributionUrl").hide();
      }
    }
  },
  
  // Event handlers
  onCancel: function(){
    this.onClose();
  },
  
  onClose: function(){
    this.setProgressBarColor(this.statusBarColor);
    this.close();
  },
  
  onApiKeySubmit: function(){
    var me = this;
    var apiKey = me.down("textfield[name=apiKey]").getValue();
    
    if(!apiKey){
      return;
    }
    
    me.progressBar.updateProgress(0.3, __("Validating API key..."));
    
    // Save API key
    me.saveAPIToken(apiKey).then(
      function(){
        me.stateData.apiKey = apiKey;
        me.progressBar.updateProgress(0.4, __("API key saved"));
        me.transitionTo(null, "success");
      },
      function(error){
        me.stateData.error = __("Failed to save API key: ") + error;
        me.transitionTo(null, "failure");
      },
    );
  },
  
  onDescriptionBack: function(){
    this.transitionTo(this.STATE_ENTER_API_KEY);
  },
  
  onDescriptionSubmit: function(){
    var me = this;
    var description = me.down("textarea[name=description]").getValue() || "";
    
    me.progressBar.updateProgress(0.7, __("Sending contribution..."));
    
    // Send contribution
    me.doContrib(me.stateData.apiKey, me.stateData.sharedInfo, description).then(
      function(result){
        me.stateData.url = result.url;
        me.progressBar.updateProgress(0.9, __("Contribution sent"));
        me.transitionTo(null, "success");
      },
      function(error){
        me.stateData.error = __("Failed to send contribution: ") + error;
        me.transitionTo(null, "failure");
      },
    );
  },
  
  onOpenContribution: function(){
    if(this.stateData.url){
      window.open(this.stateData.url, "_blank");
    }
  },

  setProgressBarColor: function(color){
    this.progressBar.getEl().dom.querySelector("[id$='-bar']").style.backgroundColor = color;
  },

  getProgressBarColor: function(){
    return window.getComputedStyle(this.progressBar.getEl().dom.querySelector("[id$='-bar']")).backgroundColor;
  },
  // ajax requests
  getAPIToken: function(){
    var url = this.apiTokenEndpoint,
      failureCb = this.failureCb;
    return new Promise(function(resolve, reject){
      Ext.Ajax.request({
        url: url, 
        method: "GET",
        scope: this,
        success: function(response){
          var data = Ext.decode(response.responseText);
          if(data && data.token){
            resolve(data.token)
          } else{
            reject(__("No API token found"));
          }
        },
        failure: failureCb(reject),
      })
    });
  },
  
  saveAPIToken: function(token){
    var url = this.apiTokenEndpoint,
      failureCb = this.failureCb;
    return new Promise(function(resolve, reject){
      Ext.Ajax.request({
        url: url,
        method: "POST",
        jsonData: {
          token: token,
        },
        scope: this,
        success: function(){
          resolve()
        },
        failure: failureCb(reject),
      });
    });
  },
  
  getSharedInfo: function(){
    var url = this.restUrl,
      failureCb = this.failureCb;
    return new Promise(function(resolve, reject){
      Ext.Ajax.request({
        url: url,
        method: "GET",
        success: function(response){
          try{
            var result = Ext.decode(response.responseText);
            if(Ext.isDefined(result.path)){
              resolve(result);
            } else{
              reject(result.error || __("Unknown error"));
            }
          } catch(error){
            console.error(error);
            reject(__("Invalid response format"));
          }
        },
        failure: failureCb(reject),
      });
    });
  },
 
  doContrib: function(apiKey, info, description){
    var url = this.getnocAPIContribURL,
      failureCb = this.failureCb;
    return new Promise(function(resolve, reject){
      Ext.Ajax.request({
        url: url,
        method: "POST",
        headers: {
          "Authorization": "Bearer " + apiKey,
        },
        jsonData: {
          title: info.title,
          description: description,
          content: [
            {
              path: info.path,
              content: info.content,
            },
          ],
        },
        success: function(response){
          try{
            var result = Ext.decode(response.responseText);
            if(result.status){
              resolve({
                url: result.url,
              });
            } else{
              reject(result.msg || "Unknown error");
            }
          } catch(error){
            console.error(error);
            reject("Invalid response format");
          }
        },
        failure: failureCb(reject),
      });
    });
  },
  // Handle failure
  failureCb: function(reject){
    return function(response){
      reject(__("Request failed with status") + " :" + response.status);
    }
  },
});