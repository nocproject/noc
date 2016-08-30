Ext.define 'Report.widget.Base',
	extend: 'Ext.panel.Panel'
	xtype: 'widgetBase'

	title: 'Виджет'
	cls: 'widget-base'
	shadow: true
	draggable: true
	bodyPadding: 12

	tools: [
		{
			type: 'gear',
			# TODO callback: 'showSettings'
		}
	]

	showSettings: () ->
		Ext.create @getSettingsType(), {widget: @}