Ext.application(
	extend: 'Ext.app.Application'
	name: 'Report'
	
	requires: [
		'Report.view.root.Main'
	]
	
	controllers: [
		'Configurator'
		'Dashboard'
		'Library'
		'Root'
		'Widget'
	]
	
	mainView: 'Report.view.root.Main'
	
	launch: () ->
		@getController('Root').makeReport()
)