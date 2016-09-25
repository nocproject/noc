###
    Управление виджетами.
###
Ext.define 'Report.controller.Widget',
	extend: 'Ext.app.Controller'
	id: 'widget'
	
	control:
		component:
			'widgetLibrary #control #create':
				click: 'showConfigurator'
			'widgetLibrary #control #select':
				click: 'addWidget'

	###
		Показывает конфигуратор виджета.
	###
	showConfigurator: () ->
		Ext.create 'Report.view.widget.Configurator'

		# TODO ???
	
	###
		Добавляет виджет в дашборд.
        @param {Ext.button.Button} button Кнопка добавления дашборда.
	###
	addWidget: (button) ->
		list = button.up('widgetLibrary').down('#list')
		widgetData = list.getSelectionModel().getSelection()[0]
		
		###
		    Оповещает о необходимости добавления виджета.
            @param {Report.controller.Widget} this Контроллер.
            @param {Report.model.config.Widget} widgetData Данные виджета.
		###
		@fireEvent 'addWidgetAction', @, widgetData