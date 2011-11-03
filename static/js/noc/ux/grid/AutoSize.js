Ext.define('Ext.ux.grid.AutoSize', {
    alias : 'plugin.autosizegrid',

    rowHeight: 0,

    constructor :  function(config) {
        Ext.apply(this, config);
    },

    init : function(gridpanel) {
        gridpanel.on('resize', this.onResize, this);
        gridpanel.getView().on('refresh', this.onRefresh, this);
    },

    onResize: function(gridpanel) {
        this.update_content(gridpanel.getView());
    },

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
