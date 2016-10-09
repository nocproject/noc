###
	Основа дашборда.
###
Ext.define 'Report.view.dashboard.Main',
	extend: 'Ext.panel.Panel'
	xtype: 'dashboardMain'

	requires: [
		'Report.view.dashboard.Configurator'
		'Report.view.dashboard.Library'
	]
	
	layout: 'fit'
	
	config:
	
		###
			@cfg {Ext.data.Model} model Модель-конфиг дашборда.
		###
		model: null
		
		###
			@cfg {Number} dashPadding Отступ внутренностей дашборда.
		###
		dashPadding: 10
		
		###
			@cfg {Number} dashCellHeight Высота ячейки дашборда.
		###
		dashCellHeight: 310
		
		###
			@cfg {Number} dashColumns Количество колонок дашборда.
		###
		dashColumns: 4
		
		###
			@cfg {Number} dashHeaderHeight Высота хедера виджета.
		###
		dashHeaderHeight: 56
		
		###
			@cfg {Boolean} dashFirstCall Первый ли запуск отрисовки дашборда.
		###
		dashFirstCall: true
		
	items: [
		{
			xtype: 'container'
			scrollable: 'vertical'
			items: [
				{
					itemId: 'widgets'
					xtype: 'panel'
					layout:
						type: 'hbox'
						align: 'center'
						pack: 'center'
				}
			]
		}
	]
	
	dockedItems: [
		{
			xtype: 'container'
			layout: 'hbox'
			padding: '10 12 10 0'
			items: [
				{
					xtype: 'component'
					flex: 1
				}
				{
					itemId: 'addWidget'
					xtype: 'button'
					iconCls: 'x-fa fa-plus'
					text: 'Виджет'
					margin: '2 10 0 0'
				}
				{
					itemId: 'configure'
					xtype: 'button'
					iconCls: 'x-fa fa-gear'
					text: 'Настроить'
					margin: '2 10 0 0'
				}
				{
					itemId: 'close'
					xtype: 'button'
					iconCls: 'x-fa fa-close'
					text: 'Закрыть'
				}
			]
		}
	]

	initComponent: () ->
		@callParent arguments
		
		@down('#widgets').on {
			resize:      () => @fixScrollOnResize()
			afterrender: () => @doDashboardLayout()
		}
	
	###
		Запуск расстановки виджетов внутри дашборда.
	###
	doDashboardLayout: () ->
		items = @getDashItems()
		cursor = @makeNewCursor()
		matrix = @generateEmptyMatrix()
		cursorMove = @makeCursorToFreeMover matrix, cursor
		populate = @makeFiller matrix, cursor

		for item in items

			width = item.getBoardWidth()
			height = item.getBoardHeight()

			cursorMove width
			populate width, height

			@setDashItemSize item, width, height
			@moveDashItem(
				@positioning cursor, width
				item
			)

	privates:

		###
			Фикс скрола при ресайзе дашборда.
			Исправляет проблему с недостаточным отступом снизу.
		###
		fixScrollOnResize: do () ->
			browserCall = false
			() ->
				browserCall = !browserCall

				if browserCall
					@setHeight @getHeight() + @getQuadDashPadding()

		###
			Генерация пустой виртуальной матрицы расположения элементов.
			Используется для расстановки элементов без учета конкретных размеров.
			Каждый виджет может занимать в матрице несколько ячеек.
			@return {Array[]} Пустая матрица.
		###
		generateEmptyMatrix: () ->
			matrix = []

			for column in [0...@getDashColumns()]
				matrix.push []

				for cell in [0...100]
					matrix[column][cell] = false

			matrix

		###
			Создает пустой курсор для хранения текущей позиции в
			матрице виджетов при рассчете расстановки.
			@return {Object} Курсор.
		###
		makeNewCursor: () ->
			{
				col: 0
				row: 0
			}

		###
			Возвращает виджеты дашборда.
			@return {Ext.Component[]} Виджеты.
		###
		getDashItems: () ->
			@down('#widgets').items

		###
			Возвращает ширину колонки лейаута в пикселях.
			@return {Number} Ширина.
		###
		getColWidth: () ->
			@getWidth() / @getDashColumns()

		###
			Выполняет позиционирование виджета на доске.
			@param {Object} cursor Курсор.
			@param {Number} width Ширина в виртуальных единицах.
			@return {Function}
			Функция, принимающая первым параметром виджет (Ext.Component).
		###
		positioning: (cursor, width) -> (item) =>
			x = @calcX cursor.col, width
			y = @calcY cursor.row

			@toEndOfTurn () =>
				item.setLocalXY x, y
				item.on 'move', @doDashboardLayout, @, {single: true}

				@doDashboardLayoutAgainIfFirstCall()

		###
			Помещает функцию в конец очереди исполнения интерпретатором JS.
			@param {Function} fn Функция.
		###
		toEndOfTurn: (fn) ->
			setTimeout fn, 0

		###
			Вычисляет X-координату для виджета.
			@param {Number} col Колонка.
			@param {Number} width Ширина в виртуальных единицах.
			@return {Number} Координата.
		###
		calcX: (col, width) ->
			@getColWidth() * col + width + @getDashPadding()

		###
			Вычисляет Y-координату для виджета.
			@param {Number} row Строка.
			@return {Number} Координата.
		###
		calcY: (row) ->
			@getDashCellHeight() * row - @getDashHeaderHeight() * row + @getDoubleDashPadding()

		###
			Заново запускает расстановку виджетов если был произведен первый запуск расстановки.
		###
		doDashboardLayoutAgainIfFirstCall: () ->
			if @getDashFirstCall()
				@setDashFirstCall false
				@doDashboardLayout()

		###
			Перемещает элемент дашборада на доске.
			Не предполагает ручной вызов, метод служит
			для работы при расстановке виджетов на доске.
			@param {Function} move Функция-передвигатель.
			@param {Ext.Component} item Виджет.
		###
		moveDashItem: (move, item) ->
			if item.rendered
				move item
			else
				item.on 'afterrender', move, @

		###
			Удвоенный отступ доски.
			@return {Number} Отступ.
		###
		getDoubleDashPadding: () ->
			@getDashPadding() * 2
	
		###
			Четверной отступ доски.
			@return {Number} Отступ.
		###
		getQuadDashPadding: () ->
			@getDoubleDashPadding() * 2
	
		###
			Особый отступ доски по высоте, особенность рендеринга.
			@return {Number} Отступ.
		###
		getMagicHeightDashPadding: () ->
			@getDashPadding() * 7.5
	
		###
			Устанавливает физические размеры виджета в пикселях.
			@param {Ext.Component} item Виджет.
			@param {Number} width Ширина в виртуальных единицах.
			@param {Number} height Высота в виртуальных единицах.
		###
		setDashItemSize: (item, width, height) ->
			@setDashItemWidth item, width
			@setDashItemHeight item, height
	
		###
			Устанавливает физическую ширину виджета в пикселях.
			@param {Ext.Component} item Виджет.
			@param {Number} width Ширина в виртуальных единицах.
		###
		setDashItemWidth: (item, width) ->
			item.setWidth @calcDashItemWidth width
	
		###
			Вычисляет необходимую ширину виджета в пикселях.
			@param {Number} width Ширина.
			@return {Number} Результат вычислений.
		###
		calcDashItemWidth: (width) ->
			width * @getColWidth() - @getDoubleDashPadding()
	
		###
			Устанавливает физическую высоту виджета в пикселях.
			@param {Ext.Component} item Виджет.
			@param {Number} height Высота в виртуальных единицах.
		###
		setDashItemHeight: (item, height) ->
			item.setHeight @calcDashItemHeight height
	
		###
			Вычисляет необходимую высоту виджета в пикселях.
			@param {Number} height Высота.
			@return {Number} Результат вычислений.
		###
		calcDashItemHeight: (height) ->
			total = height * @getDashCellHeight()
			header = @getDashHeaderHeight() * (height - 1)
			padding = @getMagicHeightDashPadding()

			total - header - padding
	
		###
			Создает функцию, устанавливающую курсор на свободную позицию в матрице
			с учетов виртуальных размеров виджета, пропуская занятые ячейки и ячейки,
			установка в которую приведет к залезанию на другой виджет или выход за границы доски.
			@param {Array[]} matrix Матрица.
			@param {Object} cursor Курсор.
			@return {Function} Функция, принимающая первым параметром шиниру, в Number.
		###
		makeCursorToFreeMover: (matrix, cursor) -> (width) =>
			loop
				if @isDashOverflow cursor, width
					@nextRow cursor
					continue

				if @isEngaged matrix, cursor
					@nextCol cursor
					continue

				break
	
		###
			Определяет получится ли переполнение при установке виджета
			по указанному курсором адресу в матрице.
			@param {Object} cursor Курсор.
			@param {Number} width Ширина.
			@return {Boolean} Результат проверки.
		###
		isDashOverflow: (cursor, width) ->
			cursor.col + width > @getDashColumns()
	
		###
			Определяет занята ли ячейка матрицы по адресу, указанному курсором.
			@param {Array[]} matrix Матрица.
			@param {Object} cursor Курсор.
			@return {Boolean} Результат проверки.
		###
		isEngaged: (matrix, cursor) ->
			matrix[cursor.col][cursor.row]
	
		###
			Переводит курсор на следующую строку матрицы.
			@param {Object} cursor Курсор.
		###
		nextRow: (cursor) ->
			cursor.col = 0
			cursor.row = cursor.row + 1
	
		###
			Переводит курсор на следующую колонку матрицы.
			@param {Object} cursor Курсор.
		###
		nextCol: (cursor) ->
			cursor.col = ++cursor.col
	
		###
			Создает функцию-заполнятель, которая заполняет пространство
			в матрице виджетов на указанные высоту и ширину.
			@param {Array[]} matrix Матрица.
			@param {Object} cursor Курсор.
			@return {Function}
			Функция, принимающая на вход 2 параметра - шарину и высоту, оба Number.
		###
		makeFiller: (matrix, cursor) -> (width, height) =>
			for colIndex in [0...width]
				col = cursor.col + colIndex
				row = cursor.row

				matrix[col][row] = true

				for rowIndex in [0...height]
					row = cursor.row + rowIndex

					matrix[col][row] = true