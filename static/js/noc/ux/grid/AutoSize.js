Ext.define('Ext.ux.grid.AutoSize', {
    alias : 'plugin.autosizegrid',

    rowHeight: 0,

    constructor :  function(config) {
        Ext.apply(this, config);
    },

    init : function(gridpanel) {
        gridpanel.getView().on('refresh', this.onRefresh, this);
        gridpanel.on('added', this.onAdded, this);
    },

    // listen parent's 'resize' event
    onAdded : function(gridpanel) {
        gridpanel.ownerCt.on('resize', this.onResize, this);
    },

    onResize: function(panel) {
        this.update_content(panel.down('gridpanel').getView());
    },

    // calculate row size when grid displayed first time
    onRefresh: function(view) {
        var e = view.all.item(0);

        if(!e) { return; }

        this.rowHeight = e.getHeight();
        this.update_content(view);
        view.un('refresh', this.onRefresh, this);
    },

    update_content: function(view) {
        if (this.rowHeight != 0) {
            var new_pageSize = Math.floor(view.getHeight()/this.rowHeight);

            if (view.store.pageSize != new_pageSize) {
                view.store.pageSize = new_pageSize;
                view.store.load();
            }
        }
    }
});
