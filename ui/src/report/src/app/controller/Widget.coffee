###
	Управление виджетами.
    TODO При удалении выбирать предыдущий пункт в библиотеке.
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
			'widgetLibrary #control #edit':
				click: 'configureWidgetFromLibrary'
			'widgetLibrary #control #copy':
				click: 'copyWidget'
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
			Конфигурирует выбранный виджет из библиотеки виджетов.
			Поддерживает массовую конфигурацию, открывая множество окон конфигурации.
			@param {Ext.button.Button} button Кнопка конфигурации виджета.
		###
		configureWidgetFromLibrary: (button) ->
			@forSelectedInLibrary button, (widgetData) =>
				Ext.create 'Report.view.widget.Configurator',
					entityType: @ENTITY_TYPE
					entityModel: widgetData
					
		###
			Копирует выбранный виджет дашборда, поддерживает массовое копирование.
			@param {Ext.button.Button} button Кнопка копирования дашборда.
		###
		copyWidget: (button) ->
			@forSelectedInLibrary button, (widgetData, widgets) =>
				data = widgetData.getData()
				
				delete data.id
				data.visible = false
				data.name += ' (копия)'
				
				widgets.add data
			                                    
		###
			Удаляет выбранный виджет из дашборда, поддерживается массовое удаление.
			@param {Ext.button.Button} button Кнопка удаления дашборда.
		###
		deleteWidget: (button) ->
			@forSelectedInLibrary button, (widgetData, widgets) =>
				widgets.remove widgetData
			
			@fireEvent 'refresh', @
	
		###
			Итерируется по выбранным вилжетам в библиотеке виджетов.
			@param {Ext.component.Component} component Любой компонент, лежащий внутри библиотеки.
			@param {Function}
			Функция, принимающая первым аргументом модель, относящуюся к выбранному виджету
			в библиотеке виджетов, а вторым аргументом принимает стор, хранящий все виджеты текущего дашборда.
		###
		forSelectedInLibrary: (component, fn) ->
			library = component.up('widgetLibrary')
			list = library.down('#list')
			selected = list.getSelected()
			widgets = @getWidgets()
			
			return unless widgets
			
			for widgetData in selected
				fn widgetData, widgets
		
		###
			@return {Ext.data.Store/Null}
            Стор, хранящий виджеты либо null если ни один из дашбордов не активен.
		###
		getWidgets: () ->
			dashboards = Report.model.MainDataTree.get('dashboards')
			dashboards.findRecord('active', true)?.get('widgets')