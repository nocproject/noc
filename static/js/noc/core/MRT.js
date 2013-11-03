//---------------------------------------------------------------------
// Map/Reduce task abstraction
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.MRT");

Ext.define("NOC.core.MRT", {
    mixins: {
        observable: 'Ext.util.Observable'
    },
    // scope: null,
    url: null,
    taskId: null,
    success: null,
    failure: null,
    showProgress: true,
    _loadMask: false,
    loadMask: false,

    constructor: function(config) {
        config = config || {};
        Ext.apply(this, config);
        this.addEvents(
            "beforetask",
            "taskcomplete",
            "taskexception",
            "check"
        );
        this.mixins.observable.constructor.call(this);
    },
    // Run new MRT
    run: function() {
        var me = this,
            data = {selector: me.selector};

        if(me.mapParams)
            data.map_params = me.mapParams;
        me.mask();
        if(me.fireEvent("beforetask", me) !== false ) {
            Ext.Ajax.request({
                url: me.url,
                method: "POST",
                scope: me,
                jsonData: data,
                success: function(response) {
                    this.taskId = Ext.decode(response.responseText);
                    me.checkMRT();
                },
                failure: function() {
                    me.unmask();
                    this.fireEvent("taskexception", this);
                    Ext.callback(me.failure, me.scope, []);
                }
            });
        }
    },
    // Check running MRT
    checkMRT: function() {
        var me = this;

        Ext.Ajax.request({
            url: me.url + me.taskId + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var r = Ext.decode(response.responseText);
                if(r.ready) {
                    // MRT Finished
                    me.unmask();
                    this.fireEvent("taskcomplete", this, [r.result]);
                    Ext.callback(me.success, me.scope, [r.result]);
                } else
                    // Wait and recheck
                    Ext.defer(Ext.bind(me.checkMRT, me), 1000);
            },
            failure: function() {
                me.unmask();
                this.fireEvent("taskexception", this);
                Ext.callback(me.failure, me.scope);
            }
        });
    },
    // Show wait... mask
    mask: function() {
        var me = this;

        if(me.showProgress) {
            me._loadMask = new Ext.LoadMask(me.loadMask || Ext.getBody(), {
                msg: "Running task. Please wait ..."});
            me._loadMask.show();
        }
    },
    // Hide wait... mask
    unmask: function() {
        var me = this;
        if(me._loadMask) {
            me._loadMask.hide();
        }
    }
});
