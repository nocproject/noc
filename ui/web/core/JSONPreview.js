//---------------------------------------------------------------------
// NOC.core.JSONPreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.JSONPreview");

Ext.define("NOC.core.JSONPreview", {
  extend: "Ext.panel.Panel",
  msg: "",
  layout: "fit",
  app: null,
  restUrl: null,
  previewName: null,
  apiPrefix: null,
  getnocAPIContribURL: "https://api.getnoc.com/api/v1/contrib",
  gitlabAPIToken: null,
  sharedInfo: null,
  // Progress Steps
  SS_START: 0,
  SS_ASK_API_KEY: 1,
  SS_SAVE_API_KEY: 2,
  SS_GET_SHARE_INFO: 3,
  SS_GET_DESCRIPTION: 4,
  SS_CONTRIB: 5,

  shareState: [
    // SS_START
    {
      value: 0.0,
      text: __("Getting API key"),
    },
    // SS_ASK_API_KEY
    {
      value: 0.1,
      text: __("Asking API key"),
    },
    // SS_SAVE_API_KEY
    {
      value: 0.1,
      text: __("Saving API key"),
    },
    // SS_GET_SHARE_INFO
    {
      value: 0.1,
      text: __("Getting share info"),
    },
    // SS_GET_DESCRIPTION
    {
      value: 0.1,
      text: __("Getting details"),
    },
    // SS_CONTRIB
    {
      value: 0.6,
      text: __("Contributing"),
    },
  ],

  initComponent: function(){
    var me = this,
      tb = [],
      collection = me.app.noc.collection;

    // Close button
    tb.push(Ext.create("Ext.button.Button", {
      text: __("Close"),
      glyph: NOC.glyph.arrow_left,
      scope: me,
      handler: me.onClose,
    }));
    //
    me.shareButton = Ext.create("Ext.button.Button", {
      text: __("Share"),
      glyph: NOC.glyph.share,
      scope: me,
      handler: me.onShare,
    });

    me.shareProgress = Ext.create("Ext.ProgressBar", {
      width: 500,
      hidden: true,
    });

    me.saveButton = Ext.create("Ext.button.Button", {
      text: __("Save"),
      glyph: NOC.glyph.save,
      scope: me,
      handler: me.onSave,
    });
  
    if(collection && NOC.settings.collections.allow_sharing && NOC.hasPermission("create")){
      tb.push("-");
      tb.push(me.shareButton);
      tb.push(me.shareProgress);
    }

    if(collection && NOC.settings.collections.allow_overwrite){
      tb.push("-");
      tb.push(me.saveButton);
    }

    me.cmContainer = Ext.create({
      xtype: "container",
      layout: "fit",
      tpl: [
        '<div id="{cmpId}-cmEl" class="{cmpCls}" style="{size}"></div>',
      ],
      data: {
        cmpId: me.id,
        cmpCls: Ext.baseCSSPrefix + "codemirror " + Ext.baseCSSPrefix + 'html-editor-wrap ' + Ext.baseCSSPrefix + 'html-editor-input',
        size: "width:100%;height:100%",
      },
    });

    Ext.apply(me, {
      dockedItems: [{
        xtype: "toolbar",
        dock: "top",
        items: tb,
      }],
      items: [me.cmContainer],
    });
    me.callParent();
  },
  //
  afterRender: function(){
    var me = this;
    me.callParent(arguments);
    me.initViewer();
  },
  //
  initViewer: function(){
    var me = this,
      el = me.cmContainer.el.getById(me.id + "-cmEl", true);
    // Create CodeMirror
    me.viewer = new CodeMirror(el, {
      readOnly: true,
      lineNumbers: true,
      styleActiveLine: true,
      matchBrackets: true,
    });
    // change the codemirror css
    var css = Ext.util.CSS.getRule(".CodeMirror");
    if(css){
      css.style.height = "100%";
      css.style.position = "relative";
      css.style.overflow = "hidden";
    }
    css = Ext.util.CSS.getRule('.CodeMirror-Scroll');
    if(css){
      css.style.height = '100%';
    }
    me.setTheme(NOC.settings.preview_theme);
  },
  // Set CodeMirror theme
  setTheme: function(name){
    var me = this;
    if(name !== "default"){
      Ext.util.CSS.swapStyleSheet(
        "cmcss-" + me.id, // Fake one
        "/ui/pkg/codemirror/theme/" + name + ".css",
      );
    }
    me.viewer.setOption("theme", name);
  },
  //
  renderText: function(text, syntax){
    var me = this;
    syntax = syntax || null;
    CodeMirror.modeURL = "/ui/pkg/codemirror/mode/%N/%N.js";
    me.viewer.setValue(text);
    if(syntax){
      me.viewer.setOption("mode", syntax);
      CodeMirror.autoLoadMode(me.viewer, syntax);
    }
  },
  //
  preview: function(record){
    var me = this;
    if(!record){
      me.items.first().update("No data!!!");
      me.shareButton.setDisabled(true);
      return;
    }
    var url = me.restUrl.apply(record.data);
    me.setTitle(me.previewName.apply(record.data));
    me.currentRecord = record;
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: me,
      success: function(response){
        var json = Ext.decode(response.responseText);
        me.renderText(json, "javascript");
        me.shareButton.setDisabled(!record.get("uuid"));
      },
      failure: function(){
        NOC.error(__("Failed to get JSON"))
      },
    });
  },
  //
  onClose: function(){
    var me = this;
    me.app.showForm();
  },
  //
  onShare: function(){
    var me = this;
    Ext.Msg.show({
      title: __("Share item?"),
      msg: __("Would you like to share item and contribute to Open-Source project?"),
      buttons: Ext.Msg.YESNO,
      modal: true,
      fn: function(button){
        if(button === "yes"){
          me.doShare()
        }
      },
    })
  },
  //
  setSharingState: function(state){
    var me = this;
    me.shareProgress.setValue(me.shareState[state].value);
    me.shareProgress.updateText(me.shareState[state].text);
  },
  //
  doShare: function(){
    var me = this;
    me.shareProgress.show();
    me.setupAPIToken().then(function(result){
      return me.getSharedInfo()
    }).then(function(result){
      return me.getShareDescription()
    }).then(function(result){
      return me.doContrib()
    }).then(function(result){
      NOC.info("Shared");
      me.shareProgress.hide();
      me.sharedInfo = null;
      window.open(result, "_blank")
    }).catch(function(err){
      NOC.error(err);
      me.shareProgress.hide();
      me.sharedInfo = null;
    });
  },
  // Get or ask API token
  setupAPIToken: function(){
    var me = this;
    me.setSharingState(me.SS_START);
    return new Ext.Promise(function(resolve, reject){
      me.getAPIToken().then(
        function(value){
          me.gitlabAPIToken = value;
          resolve()
        },
        function(err){
          me.askAPIToken().then(resolve)
        });
    })
  },
  //
  getAPIToken: function(){
    var me = this;
    return new Ext.Promise(function(resolve, reject){
      Ext.Ajax.request({
        url: "/main/apitoken/noc-gitlab-api/",
        method: "GET",
        scope: me,
        success: function(response){
          var data = Ext.decode(response.responseText);
          if(data && data.token){
            resolve(data.token)
          } else{
            reject()
          }
        },
        failure: function(response){
          reject()
        },
      })
    })
  },
  //
  saveAPIToken: function(value){
    var me = this;
    me.setSharingState(me.SS_SAVE_API_KEY);
    return new Ext.Promise(function(resolve, reject){
      Ext.Ajax.request({
        url: "/main/apitoken/noc-gitlab-api/",
        method: "POST",
        jsonData: {
          token: value,
        },
        scope: me,
        success: function(response){
          resolve()
        },
        failure: function(response){
          reject(__("Cannot save API token"))
        },
      })
    })
  },
  //
  askAPIToken: function(){
    var me = this;
    me.setSharingState(me.SS_ASK_API_KEY);
    return new Ext.Promise(function(resolve, reject){
      Ext.Msg.prompt(
        "Enter Gitlab API key",
        "",
        function(button, value){
          if(button === "ok"){
            me.saveAPIToken(value).then(
              function(){
                me.gitlabAPIToken = value;
                resolve()
              }, function(){
                reject()
              })
          } else{
            reject(__("No API token given"))
          }
        },
        me,
        false,
        null,
        {
          placeHolder: "Enter API key",
        },
      )
    })
  },
  // Getting sharing information
  getSharedInfo: function(){
    var me = this;
    me.setSharingState(me.SS_GET_SHARE_INFO);
    var url = me.restUrl.apply(me.currentRecord.data).replace("/json/", "/share_info/");
    return new Ext.Promise(function(resolve, reject){
      Ext.Ajax.request({
        url: url,
        method: "GET",
        scope: me,
        success: function(response){
          me.sharedInfo = Ext.decode(response.responseText);
          resolve("OK")
        },
        failure: function(response){
          reject("Failed to get sharing info")
        },
      })
    })
  },
  //
  getShareDescription: function(){
    var me = this;
    me.setSharingState(me.SS_GET_DESCRIPTION);
    return new Ext.Promise(function(resolve, reject){
      Ext.Msg.prompt(
        "Enter Description",
        "Please enter optional contribution description",
        function(button, value){
          if(button === "ok"){
            me.sharedInfo.description = value || "";
            resolve()
          } else{
            reject(__("Cancelled"))
          }
        },
        me,
        true,
        null,
        {
          placeHolder: "Optional contribution description",
        },
      )
    })
  },
  // Send contribution
  doContrib: function(){
    var me = this;
    me.setSharingState(me.SS_CONTRIB);
    return new Ext.Promise(function(resolve, reject){
      Ext.Ajax.request({
        url: me.getnocAPIContribURL,
        method: "POST",
        headers: {
          "Private-Token": me.gitlabAPIToken,
        },
        scope: me,
        jsonData: {
          title: me.sharedInfo.title,
          description: me.sharedInfo.description,
          content: [
            {
              path: me.sharedInfo.path,
              content: me.sharedInfo.content,
            },
          ],
        },
        success: function(response){
          var data = Ext.decode(response.responseText);
          if(data.status){
            resolve(data.url)
          } else{
            reject(data.msg)
          }
        },
        failure: function(response){
          reject("Failed to contribute")
        },
      })
    })
  },
  onSave: function(){
    var me = this;
    Ext.Ajax.request({
      url: me.restUrl.apply(me.currentRecord.data),
      method: "POST",
      scope: me,
      success: function(response){
        NOC.info(__("JSON saved"));
      },
      failure: function(){
        NOC.error(__("Failed to save JSON"))
      },
    });
  },
});
