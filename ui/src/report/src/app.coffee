Ext.application(
	extend: 'Ext.app.Application'
	name: 'Report'
	
	controllers: [
		'Configurator'
		'Dashboard'
		'Filter'
		'Library'
		'Root'
		'Widget'
	]
	
	mainView: 'Report.view.root.Main'
	
	launch: () ->
		@getController('root').renderByConfig()
)