Ext.define 'Report.board.Board',
	extend: 'Ext.dashboard.Dashboard'
	xtype: 'board'
	requires: [
	    'Report.board.Menu'
	]

	tbar:
		xtype: 'boardMenu'
		listeners:
			addWidget: 'showWidgetLibrary'

	config:
		widgetLibraryWindow: null

	showWidgetLibrary: () ->
		library = @getWidgetLibraryWindow()

		if not library
			library = @createWidgetLibrary()
			@setWidgetLibraryWindow library

		library.show()

	createWidgetLibrary: () ->
		Ext.create 'Report.library.Library',
			listeners:
				addWidget: 'addWidget'

	addWidget: (library, model) ->
        #TODO