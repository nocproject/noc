//---------------------------------------------------------------------
// main.desktop application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.Application");
Ext.define("NOC.main.desktop.Application", {
    extend: "Ext.Viewport",
    layout: "border",
    requires: [
        "Ext.ux.form.SearchField",
        "NOC.core.TagsField",
        "NOC.core.StringListField",
        "NOC.core.StateField",
        "Ext.ux.form.GridField",
        "Ext.ux.form.DictField",
        "Ext.ux.form.ColorField",
        "Ext.ux.grid.column.GlyphAction",
        "NOC.core.CMText"
    ],

    initComponent: function() {
        var me = this;
        me.restartReason = null;
        me.templates = NOC.templates["main_desktop"];
        // Setup helpers
        NOC.run = Ext.bind(me.launchTab, me);
        NOC.launch = Ext.bind(me.launchApp, me);
        //
        me.launchedTabs = {};
        me.idleTimeout = 0;
        me.idleTimerId = -1;
        //
        me.navStore = Ext.create("Ext.data.TreeStore", {
            root: {
                id: "root",
                text: __("All"),
                expanded: true,
                children: []
            }
        });
        // Create panels
        me.headerPanel = Ext.create("NOC.main.desktop.HeaderPanel", {app: me});
        me.navPanel = Ext.create("NOC.main.desktop.NavPanel", {
            app: me,
            store: me.navStore
        });
        me.breadcrumbs = Ext.create("NOC.main.desktop.Breadcrumbs", {
            app: me,
            store: me.navStore
        });
        me.workplacePanel = Ext.create("NOC.main.desktop.WorkplacePanel", {app: me});
        //
        Ext.apply(me, {
            items: [
                me.headerPanel,
                me.breadcrumbs,
                me.navPanel,
                me.workplacePanel
            ]
        });
        me.callParent();
        // Set unload handler
        Ext.EventManager.addListener(window, "beforeunload",
            me.onUnload, me, {normalized: false});
    },
    //
    afterRender: function() {
        var me = this;
        me.callParent();
        console.log("NOC application ready");
        me.hideSplashScreen();
        me.checkLogged();
        me.launchAppsFromHistory();
    },
    // Launch applications from URL
    launchAppsFromHistory: function() {
        var h = Ext.History.getHash();

        if(h) {
            // Open application tab
            var p = h.split("/"),
                app = p[0],
                args = p.slice(1);
            if(args.length > 0) {
                NOC.launch(app, "history", {args: args});
            } else {
                NOC.launch(app);
            }
        }
    },
    // Show About screen
    onAbout: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/main/desktop/about/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                Ext.create("NOC.main.desktop.About", {
                    app: me,
                    aboutCfg: data
                });
            },
            failure: function() {
                NOC.error(__("Failed to get data"));
            }
        });
    },
    // Launch application from navigation record
    launchRecord: function(record, reuse) {
        var me = this,
            li;
        if(!record.isLeaf()) {
            return;
        }
        li = record.get("launch_info");
        if(li.params && li.params.link) {
            window.open(li.params.link);
        } else {
            me.launchTab(
                li.class, li.title, li.params, record.get("id"), reuse
            );
        }
    },
    // Launch application in tab
    launchTab: function(panel_class, title, params, node, reuse) {
        var me = this,
            p;
        if(reuse && node && me.launchedTabs[node]) {
            // Open tab
            me.workplacePanel.setActiveTab(me.launchedTabs[node]);
        } else {
            NOC.msg.started(__("Starting \"{0}\""), title);
            // Launch new tab
            if(!params.app_id) {
                p = panel_class.split(".");
                params.app_id = [p[1], p[2]].join(".");
            }
            var tab = me.workplacePanel.launchTab(panel_class, title, params, node);
            if (node) {
                me.launchedTabs[node] = tab;
            }
        }
    },
    launchApp: function(app, cmd, data) {
        var me = this;
        // iframe shortcut
        if(app === "iframe") {
            me.launchTab(
                "NOC.main.desktop.IFramePanel",
                data.title,
                {url: data.url}
            );
            return;
        }
        //
        // skip saved hash
        var index = app.indexOf('?')
            , _app = index === -1 ? app : app.substr(0, index)
            , url = "/" + _app.replace(".", "/") + "/launch_info/";
        Ext.Ajax.request({
            url: url,
            method: "GET",
            scope: me,
            success: function(response) {
                var li = Ext.decode(response.responseText),
                    params = {filterValuesUrl: app};
                if(cmd) {
                    params.cmd = Ext.merge({}, data);
                    params.cmd.cmd = cmd;
                }
                Ext.merge(params, li.params);
                me.launchTab(
                    li.class,
                    li.title,
                    params
                );
                // restore saved hash
                Ext.History.setHash(app);
            },
            failure: function() {
                NOC.error(__("Failed to launch application ") + " " + app);
            }
        });
    },
    // Called when application tab closed
    onCloseApp: function(menuId) {
        var me = this;
        if(me.launchedTabs[menuId]) {
            delete me.launchedTabs[menuId];
        }
    },
    // Search text entered
    onSearch: function(value) {
        var me = this;
        NOC.launch("main.search", "search", {query: value});
    },
    // Toggle all panels except workplace
    onPanelsToggle: function() {
        var me = this;
        if(me.headerPanel.isHidden()) {
            me.headerPanel.show();
            me.navPanel.show();
            me.workplacePanel.setCollapsed();
        } else {
            me.headerPanel.hide();
            me.navPanel.hide();
            me.workplacePanel.setExpanded();
        }
    },
    // Show user profile panel
    onUserProfile: function() {
        var me = this;
        NOC.run(
            "NOC.main.userprofile.Application",
            "User Profile",
            {}
        );
    },
    // Show change credentials form
    onChangeCredentials: function() {
        var me = this;
        Ext.create("NOC.main.desktop.ChangeCredentials", {
            app: me,
            fields: [
                {
                    xtype: "textfield",
                    name: "old_password",
                    fieldLabel: __("Old Password"),
                    allowBlank: false,
                    inputType: "password"
                },

                {
                    xtype: "textfield",
                    name: "new_password",
                    fieldLabel: __("New Password"),
                    allowBlank: false,
                    inputType: "password"
                },

                {
                    xtype: "textfield",
                    name: "retype_password",
                    fieldLabel: __("Retype New Password"),
                    allowBlank: false,
                    inputType: "password",
                    vtype: "password",
                    peerField: "new_password"
                }
            ]
        });
    },
    // Check session is authenticated
    checkLogged: function() {
        var me = this;
        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/is_logged/",
            scope: me,
            success: function(response) {
                var status = Ext.decode(response.responseText);
                if (status) {
                    me.onLogin();
                } else {
                    NOC.error(__("Login failed"));
                }
            },
            failure: function(response) {
                NOC.error(__("Login failed"));
            }
        });
    },
    // Called when session is authenticated or user logged in
    onLogin: function() {
        var me = this;
        // Initialize state provider
        Ext.state.Manager.setProvider(Ext.create("NOC.core.StateProvider"));
        // Apply user settings
        Ext.Ajax.request({
            method: "GET",
            url: "/main/desktop/user_settings/",
            scope: me,
            success: function(response) {
                var settings = Ext.decode(response.responseText),
                    displayName = [];
                // Save settings
                NOC.username = settings.username;
                NOC.email = settings.email;
                // Build display name
                if(settings.first_name) {
                    displayName.push(settings.first_name);
                }
                if(settings.last_name) {
                    displayName.push(settings.last_name);
                }
                if(displayName.length === 0) {
                    displayName.push(settings.username);
                }
                me.headerPanel.setUserName(displayName.join(" "));
                // Display username button
                me.headerPanel.showUserMenu(settings.can_change_credentials);
                // Reset opened tabs
                me.launchedTabs = {};
                // Set menu
                me.navStore.setRoot(settings.navigation);
                me.breadcrumbs.updateSelection("root");
                // Setup idle timer
                me.setIdleTimeout(settings.idle_timeout);
            }
        });
        // Launch welcome application
        if(!Ext.History.getHash()) {
            me.launchTab("NOC.main.welcome.Application", "Welcome", {});
        }
    },
    // Start logout sequence
    onLogout: function() {
        var me = this;
        document.location = "/api/login/logout/";
    },
    //
    // Process autologout
    //

    // Setup idle timeout
    setIdleTimeout: function(timeout) {
        var me = this;

        me.stopIdleTimer();
        me.idleTimeout = timeout * 1000;
        if(me.idleTimeout) {
            //
            console.log("Set idle timeout to", me.idleTimeout, "ms");
            me.idleTimerId = Ext.Function.defer(me.onIdle, me.idleTimeout, me);
            Ext.getDoc().on({
                scope: me,
                mousemove: me.resetIdleTimer,
                keydown: me.resetIdleTimer
            });
        }
        //
        window.NOCIdleHandler = Ext.bind(me.resetIdleTimer, me);
    },
    //
    stopIdleTimer: function() {
        var me = this;
        if(me.idleTimerId != -1) {
            clearTimeout(me.idleTimerId);
            me.idleTimerId = -1;
            Ext.getDoc().un({
                scope: me,
                mousemove: me.resetIdleTimer,
                keydown: me.resetIdleTimer
            });
        }
    },
    //
    resetIdleTimer: function() {
        var me = this;
        clearTimeout(me.idleTimerId);
        if(me.idleTimeout) {
            me.idleTimerId = Ext.Function.defer(me.onLogout, me.idleTimeout, me);
        }
    },
    //
    onUnload: function(e) {
        var me = this,
            msg = "You're trying to close NOC application. Unsaved changes may be lost.";
        if(me.restartReason) {
            return;
        }
        if(e) {
            e.returnValue = msg;
        }
        if(window.event) {
            window.event.returnValue = msg;
        }
        return msg;
    },
    //
    restartApplication: function(reason) {
        var me = this;
        me.restartReason = reason;
        window.location.reload();
    },
    // Request full-screen mode
    requestFullscreen: function() {
        var me = this,
            element = document.body,
            method = element.requestFullScreen
                || element.webkitRequestFullScreen
                || element.mozRequestFullScreen
                || element.msRequestFullScreen;
        if(method) {
            method(element);
        }
    },
    exitFullscreen: function() {
        var me = this,
            method = element.exitFullScreen
                || element.webkitExitFullScreen
                || element.mozCancelFullScreen
                || element.msExitFullScreen;
        if(method) {
            method();
        }
    },
    //
    hideSplashScreen: function() {
        var me = this,
            mask = Ext.get("noc-loading-mask"),
            parent = Ext.get("noc-loading");
        mask.fadeOut({callback: function(){mask.destroy();}});
        parent.fadeOut({callback: function(){parent.destroy();}});
    },
    //
    toggleNav: function() {
        var me = this;
        if(me.breadcrumbs.isVisible()) {
            me.breadcrumbs.hide();
            me.navPanel.show();
        } else {
            me.breadcrumbs.show();
            me.navPanel.hide();
        }
    }
});
