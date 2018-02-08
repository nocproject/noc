//---------------------------------------------------------------------
// NOC.core.JSONPreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
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
    apiTokenURL: null,
    gitlabAPIToken: null,
    gitlabUsername: null,
    //gitlabProjectName: "noc-contrib-collections",
    gitlabProjectName: "collections",
    gitlabProjectId: null,
    sharedFilePath: null,
    sharedFileExists: false,
    sharedContent: false,
    sharedBranch: null,
    MASTER_BRANCH: "master",
    // Progress Steps
    SS_START: 0,
    SS_ASK_API_KEY: 1,
    SS_SAVE_API_KEY: 2,
    SS_CHECK_GITLAB_LOGIN: 3,
    SS_CHECK_PROJECT: 4,
    SS_GET_SHARE_INFO: 5,
    SS_CHECK_FILE: 6,
    SS_CREATE_BRANCH: 7,
    SS_UPLOAD_FILE: 8,
    SS_MERGE_REQUEST: 9,

    shareState: [
        // SS_START
        {
            value: 0.0,
            text: __("Getting API key")
        },
        // SS_ASK_API_KEY
        {
            value: 0.05,
            text: __("Asking API key")
        },
        // SS_SAVE_API_KEY
        {
            value: 0.1,
            text: __("Saving API key")
        },
        // SS_CHECK_GITLAB_LOGIN
        {
            value: 0.2,
            text: __("Checking Gitlab login")
        },
        // SS_CHECK_PROJECT
        {
            value: 0.3,
            text: __("Checking project")
        },
        // SS_SHARE_INFO
        {
            value: 0.4,
            text: __("Getting sharing information")
        },
        // SS_CHECK_FILE
        {
            value: 0.5,
            text: __("Checking repository file")
        },
        // SS_CREATE_BRANCH
        {
            value: 0.6,
            text: __("Creating branch")
        },
        // SS_UPLOAD_FILE
        {
            value: 0.7,
            text: __("Uploading File")
        },
        // SS_MERGE_REQUEST
        {
            value: 0.9,
            text: __("Creating merge request")
        }
    ],

    initComponent: function() {
        var me = this,
            tb = [],
            collection = me.app.noc.collection;

        // Calculate api prefix
        if(NOC.settings.gitlab_url.endsWith("/")) {
            me.apiPrefix = NOC.settings.gitlab_url + "api/v4/";
            me.apiTokenURL = NOC.settings.gitlab_url + "profile/personal_access_token"
        } else {
            me.apiPrefix = NOC.settings.gitlab_url + "/api/v4/";
            me.apiTokenURL = NOC.settings.gitlab_url + "/profile/personal_access_token"
        }

        // Close button
        tb.push(Ext.create("Ext.button.Button", {
            text: __("Close"),
            glyph: NOC.glyph.arrow_left,
            scope: me,
            handler: me.onClose
        }));
        //
        me.shareButton = Ext.create("Ext.button.Button", {
            text: __("Share"),
            glyph: NOC.glyph.share,
            scope: me,
            handler: me.onShare
        });

        me.shareProgress = Ext.create("Ext.ProgressBar", {
            width: 500,
            hidden: true
        });

        if(collection && NOC.settings.collections.allow_sharing && NOC.hasPermission("create")) {
            tb.push("-");
            tb.push(me.shareButton);
            tb.push(me.shareProgress);
        }

        me.cmContainer = Ext.create({
            xtype: "container",
            layout: "fit",
            tpl: [
                '<div id="{cmpId}-cmEl" class="{cmpCls}" style="{size}"></div>'
            ],
            data: {
                cmpId: me.id,
                cmpCls: Ext.baseCSSPrefix + "codemirror " + Ext.baseCSSPrefix + 'html-editor-wrap ' + Ext.baseCSSPrefix + 'html-editor-input',
                size: "width:100%;height:100%"
            }
        });

        Ext.apply(me, {
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: tb
            }],
            items: [me.cmContainer]
        });
        me.callParent();
    },
    //
    afterRender: function() {
        var me = this;
        me.callParent(arguments);
        me.initViewer();
    },
    //
    initViewer: function() {
        var me = this,
            el = me.cmContainer.el.getById(me.id + "-cmEl", true);
        // Create CodeMirror
        me.viewer = new CodeMirror(el, {
            readOnly: true,
            lineNumbers: true,
            styleActiveLine: true,
            matchBrackets: true
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
    setTheme: function(name) {
        var me = this;
        if(name !== "default") {
            Ext.util.CSS.swapStyleSheet(
                "cmcss-" + me.id,  // Fake one
                "/ui/pkg/codemirror/theme/" + name + ".css"
            );
        }
        me.viewer.setOption("theme", name);
    },
    //
    renderText: function(text, syntax) {
        var me = this;
        syntax = syntax || null;
        CodeMirror.modeURL = "/ui/pkg/codemirror/mode/%N/%N.js";
        me.viewer.setValue(text);
        if(syntax) {
            me.viewer.setOption("mode", syntax);
            CodeMirror.autoLoadMode(me.viewer, syntax);
        }
    },
    //
    preview: function(record) {
        var me = this;
        if(!record) {
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
            success: function(response) {
                var json = Ext.decode(response.responseText);
                me.renderText(json, "javascript");
                me.shareButton.setDisabled(!record.get("uuid"));
            },
            failure: function() {
                NOC.error(__("Failed to get JSON"))
            }
        });
    },
    //
    onClose: function() {
        var me = this;
        me.app.showForm();
    },
    //
    onShare: function() {
        var me = this;
        Ext.Msg.show({
            title: __("Share item?"),
            msg: __("Would you like to share item and contribute to opensource project?"),
            buttons: Ext.Msg.YESNO,
            modal: true,
            fn: function(button) {
                if(button === "yes") {
                    me.doShare()
                }
            }
        })
    },
    //
    setSharingState: function(state) {
        var me = this;
        me.shareProgress.setValue(me.shareState[state].value);
        me.shareProgress.updateText(me.shareState[state].text);
    },
    //
    doShare: function() {
        var me = this;
        me.shareProgress.show();
        me.setupAPIToken().then(function(result) {
            return me.checkGitlabLogin()
        }).then(function(result) {
            return me.checkProject()
        }).then(function(result) {
            return me.getShareInfo()
        }).then(function(result) {
            return me.checkFile()
        }).then(function(result) {
            return me.createBranch()
        }).then(function(result) {
            return me.uploadFile()
        }).then(function(result) {
            return me.createMergeRequest()
        }).then(function(result) {
            NOC.info(result);
            me.shareProgress.hide()
        }).catch(function(err) {
            NOC.error(err);
            me.shareProgress.hide()
        });
    },
    // Get or ask API token
    setupAPIToken: function() {
        var me = this;
        me.setSharingState(me.SS_START);
        return new Ext.Promise(function(resolve, reject) {
            me.getAPIToken().then(
                function(value) {
                    me.gitlabAPIToken = value;
                    resolve()
                },
                function(err) {
                    me.askAPIToken().then(resolve)
                });
        })
    },
    //
    getAPIToken: function() {
        var me = this;
        return new Ext.Promise(function(resolve, reject) {
            Ext.Ajax.request({
                url: "/main/apitoken/noc-gitlab-api/",
                method: "GET",
                scope: me,
                success: function(response) {
                    var data = Ext.decode(response.responseText);
                    if(data && data.token) {
                        resolve(data.token)
                    } else {
                        reject()
                    }
                },
                failure: function(response) {
                    reject()
                }
            })
        })
    },
    //
    saveAPIToken: function(value) {
        var me = this;
        me.setSharingState(me.SS_SAVE_API_KEY);
        return new Ext.Promise(function(resolve, reject) {
            Ext.Ajax.request({
                url: "/main/apitoken/noc-gitlab-api/",
                method: "POST",
                jsonData: {
                    token: value
                },
                scope: me,
                success: function(response) {
                    resolve()
                },
                failure: function(response) {
                    reject(__("Cannot save API token"))
                }
            })
        })
    },
    //
    askAPIToken: function() {
        var me = this;
        me.setSharingState(me.SS_ASK_API_KEY);
        return new Ext.Promise(function(resolve, reject) {
            Ext.Msg.prompt(
                "Enter Gitlab API key",
                "",
                function(button, value) {
                    if(button === "ok") {
                        me.saveAPIToken(value).then(
                            function() {
                                me.gitlabAPIToken = value;
                                resolve()
                            }, function() {
                                reject()
                            })
                    } else {
                        reject(__("No API token given"))
                    }
                },
                me,
                false,
                null,
                {
                    placeHolder: "Enter API key"
                }
            )
        })
    },
    // Check user is authorized in gitlab
    checkGitlabLogin: function() {
        var me = this;
        me.setSharingState(me.SS_CHECK_GITLAB_LOGIN);
        return new Ext.Promise(function(resolve, reject) {
            Ext.Ajax.request({
                url: me.apiPrefix + "user",
                method: "GET",
                headers: {
                    "Private-Token": me.gitlabAPIToken
                },
                scope: me,
                success: function(response) {
                    var data = Ext.decode(response.responseText);
                    me.gitlabUsername = data.username;
                    me.gitlabProjectId = encodeURIComponent(me.gitlabUsername + "/" + me.gitlabProjectName);
                    resolve("OK")
                },
                failure: function(response) {
                    reject("Cannot access GitLab")
                }
            })
        })
    },
    //
    checkProject: function() {
        var me = this;
        me.setSharingState(me.SS_CHECK_PROJECT);
        return new Ext.Promise(function(resolve, reject) {
            Ext.Ajax.request({
                url: me.apiPrefix + "projects/" + me.gitlabProjectId,
                method: "GET",
                headers: {
                    "Private-Token": me.gitlabAPIToken
                },
                scope: me,
                success: function (response) {
                    var data = Ext.decode(response.responseText);
                    console.log(data);
                    resolve("OK")
                },
                failure: function (response) {
                    console.log(response.status);
                    // @todo: Check 404, fork
                    reject("Cannot access GitLab project")
                }
            })
        })
    },
    //
    getShareInfo: function() {
        var me = this;
        me.setSharingState(me.SS_GET_SHARE_INFO);
        return new Ext.Promise(function(resolve, reject) {
            Ext.Ajax.request({
                url: me.restUrl.apply(me.currentRecord.data).replace("/json/", "/share_info/"),
                method: "GET",
                scope: me,
                success: function(response) {
                    var data = Ext.decode(response.responseText);
                    me.sharedFilePath = encodeURIComponent(data.file_path);
                    me.sharedContent = data.content;
                    me.sharedBranch = "contrib-" + me.gitlabUsername + "-" + data.hash;
                    resolve()
                },
                failure: function(response) {
                    reject("Cannot get share info")
                }
            })
        })
    },
    //
    checkFile: function() {
        var me = this;
        me.setSharingState(me.SS_CHECK_FILE);
        return new Ext.Promise(function(resolve, reject) {
            Ext.Ajax.request({
                url: me.apiPrefix + "projects/" + me.gitlabProjectId + "/repository/files/" + me.sharedFilePath + "?ref=" + me.MASTER_BRANCH,
                method: "GET",
                headers: {
                    "Private-Token": me.gitlabAPIToken
                },
                scope: me,
                success: function (response) {
                    var data = Ext.decode(response.responseText);
                    me.sharedFileExists = true;
                    resolve()
                },
                failure: function (response) {
                    if(response.status === 404) {
                        me.sharedFileExists = false;
                        resolve()
                    } else {
                        reject("Cannot check repository file")
                    }
                }
            })
        })
    },
    //
    createBranch: function() {
        var me = this;
        me.setSharingState(me.SS_CREATE_BRANCH);
        return new Ext.Promise(function(resolve, reject) {
            Ext.Ajax.request({
                url: me.apiPrefix + "projects/" + me.gitlabProjectId + "/repository/branches/",
                method: "POST",
                headers: {
                    "Private-Token": me.gitlabAPIToken
                },
                jsonData: {
                    branch: me.sharedBranch,
                    ref: me.MASTER_BRANCH
                },
                scope: me,
                success: function (response) {
                    var data = Ext.decode(response.responseText);
                    console.log(data);
                    resolve()
                },
                failure: function (response) {
                    console.log(response);
                    reject("Cannot create branch")
                }
            })
        })
    },
    //
    uploadFile: function() {
        var me = this;
        me.setSharingState(me.SS_UPLOAD_FILE);
        return new Ext.Promise(function(resolve, reject) {
            Ext.Ajax.request({
                url: me.apiPrefix + "projects/" + me.gitlabProjectId + "/repository/files/" + me.sharedFilePath,
                method: me.sharedFileExists ? "PUT" : "POST",
                headers: {
                    "Private-Token": me.gitlabAPIToken
                },
                jsonData: {
                    file_path: me.sharedFilePath,
                    branch: me.sharedBranch,
                    start_branch: me.sharedBranch,
                    content: me.sharedContent,
                    commit_message: me.previewName.apply(me.currentRecord.data)
                },
                scope: me,
                success: function (response) {
                    var data = Ext.decode(response.responseText);
                    console.log(data);
                    resolve("Shared")
                },
                failure: function (response) {
                    console.log(response);
                    reject("Cannot upload file")
                }
            })
        })
    },
    //
    createMergeRequest: function() {
        var me = this;
        me.setSharingState(me.SS_MERGE_REQUEST);
        return new Ext.Promise(function(resolve, reject) {
            Ext.Ajax.request({
                url: me.apiPrefix + "projects/" + me.gitlabProjectId + "/merge_requests",
                method: "POST",
                headers: {
                    "Private-Token": me.gitlabAPIToken
                },
                jsonData: {
                    source_branch: me.sharedBranch,
                    target_branch: me.MASTER_BRANCH,
                    title: me.previewName.apply(me.currentRecord.data),
                    remove_source_branch: true
                },
                scope: me,
                success: function (response) {
                    var data = Ext.decode(response.responseText);
                    console.log(data);
                    resolve("Shared")
                },
                failure: function (response) {
                    console.log(response);
                    reject("Cannot create merge request")
                }
            })
        })
    }
});
