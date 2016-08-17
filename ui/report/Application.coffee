Ext.application(
	extend: 'Report.Application'
	name: 'Report'

	requires: [
		'Report.Viewport'
		'Report.data.Socket'
		'Report.data.Mediator'
	]

	mainView: 'Report.Viewport'
)