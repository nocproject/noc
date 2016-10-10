###
	Управление виджетами.
###
Ext.define 'Report.controller.Widget',
	extend: 'Ext.app.Controller'
	id: 'widget'

	###
		@event refresh
		Оповещает о необходимости полностью обновить отчет.
		@param {Report.controller.Widget} this Контроллер.
	###
	
	listen:
		controller:
			'#dashboard':
				addWidgetAction: 'showWidgetsLibrary'
			'#configurator':
				startSave: 'saveWidget'
		component:
			'widgetLibrary #control #create':
				click: 'showConfiguratorForLibrary'
			'widgetLibrary #control #delete':
				click: 'deleteWidget'
			'widgetLibrary #control #select':
				click: 'addWidget'
			'widgetMain #configure':
				click: 'showConfiguratorForWidget'
	
	privates:
	
		###
			@property {String} ENTITY_TYPE
			Тип сущности для конфигуратора.
			Определяется и читается в рамках контроллера, сам конфигуратор лишь хранит эту строку.
		###
		ENTITY_TYPE: 'widget'
				
		###
			Показывет библиотеку виджетов.
		###
		showWidgetsLibrary: () ->
			Ext.create(
				'Report.view.widget.Library',
				{
					entityType: @ENTITY_TYPE
				}
			).show()
	
		###
			Показывает конфигуратор виджета для создания нового виджета.
		###
		showConfiguratorForLibrary: () ->
			Ext.create 'Report.view.widget.Configurator',
				entityType: @ENTITY_TYPE
	
		###
			Показывает конфигуратор виджета для существующего виджета.
            @param {Ext.button.Button} button Кнопка конфигурирования виджета.
		###
		showConfiguratorForWidget: (button) ->
			Ext.create 'Report.view.widget.Configurator',
				entityType: @ENTITY_TYPE
				entityModel: button.up('widgetMain').getModel()
		               
		###
			Сохраняет виджет.
			@param {Report.controller.Configurator} controller Контроллер конфигуратора.
			@param {Report.model.configurator.Model} model Модель конфигуратора.
			@param {Ext.data.Model/Null} entityModel Модель сущности, которую конфигурируем, если есть.
			@param {String} entityType Тип сущности в виде произвольной строки.
		###
		saveWidget: (controller, model, entityModel, entityType) ->
			return if entityType isnt @ENTITY_TYPE
			
			dashboards = Report.model.MainDataTree.get('dashboards')
			widgets = dashboards.findRecord('active', true)?.get('widgets')
			
			return unless widgets
			
			get = model.get.bind model
			
			data = {
				name:        get 'name'
				tags:        get 'tags'
				description: get 'description'
				type:        get 'type'
				wellspring:  get 'wellspring'
				columns:     get 'columns'
				filters:     get 'filters'
				width:       get 'width'
				height:      get 'height'
			}
			
			if entityModel
				entityModel.set data
			else
				widgets.add data
			
			@fireEvent 'refresh', @
			
		###
			Добавляет виджет в дашборд.
			@param {Ext.button.Button} button Кнопка добавления дашборда.
		###
		addWidget: (button) ->
			widgets = @getWidgets()
			
			return unless widgets
			
			library = button.up('widgetLibrary')
			list = library.down('#list')
			selected = list.getSelected()
			
			for widget in selected
				widget.set('visible', true)
				widgets.add widget.getData()
			
			@fireEvent 'refresh', @
			
			library.hide()
		
		###
			Удаляет виджет из дашборда.
			@param {Ext.button.Button} button Кнопка удаления дашборда.
		###
		deleteWidget: (button) ->
			library = button.up('widgetLibrary')
			list = library.down('#list')
			selected = list.getSelected()
			widgets = @getWidgets()
			
			return unless widgets
			
			for widgetData in selected
				widgets.remove widgetData
			
			@fireEvent 'refresh', @
		
		###
			@return {Ext.data.Store/Null}
            Стор, хранящий виджеты либо null если ни один из дашбордов не активен.
		###
		getWidgets: () ->
			dashboards = Report.model.MainDataTree.get('dashboards')
			dashboards.findRecord('active', true)?.get('widgets')