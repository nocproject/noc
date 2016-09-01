Ext.define 'Report.widget.Base',
	extend: 'Ext.panel.Panel'
	xtype: 'widgetBase'

	title: 'Виджет'
	cls: 'widget-base'
	shadow: true
	# draggable: true TODO Wait for full version
	bodyPadding: 12
	width: 0
	height: 0

	tools: [
		{
			type: 'gear',
			# callback: 'showSettings' TODO Wait settings
		}
	]

	showSettings: () ->
		Ext.create @getSettingsType(), {widget: @}