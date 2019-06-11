.. _dev-handlers-window-function:

=======================
Window Function Handler
=======================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Interface for custom window functions for PM threshold processing.
Window function is a function accepting a *Window* - the list of
measures, and returning *float* value.

.. function:: window_handler(window)

    Implements custom window function

    :param window: List of (*timestamp*, *value*), where
        *timestamp* - Unix timestamp of measure
        *value* - Value of measure
    :returns: float value

Examples
--------

last
^^^^
Returns last measured value::

    def last(window):
        return window[-1][1]

finite_difference
^^^^^^^^^^^^^^^^^
Difference between last and first value::

    def finite_difference(window):
        return window[-1][1] - window[0][1]


More Examples
^^^^^^^^^^^^^
Refer to core/window.py file for more examples