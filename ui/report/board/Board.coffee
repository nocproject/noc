Ext.define 'Report.board.Board',
	extend: 'Ext.dashboard.Dashboard'
	xtype: 'board',
    requires: [
	    'Report.board.Menu'
    ]

	tbar:
		xtype: 'boardMenu'
