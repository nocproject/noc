Ext.application(
	extend: 'Ext.app.Application'
	name: 'Report'

	requires: [
		'Report.NocMenu'
		'Report.Viewport'
		'Report.data.Socket'
		'Report.data.Mediator'
		'Report.data.Ion'
	]

	mainView: 'Report.Viewport'
)