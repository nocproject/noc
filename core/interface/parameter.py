# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface parameters
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from error import InterfaceTypeError


class BaseParameter(object):
    """
    Abstract parameter
    """
    def __init__(self, required=True, default=None):
        self.required = required
        self.default = default
        if default is not None:
            self.default = self.clean(default)

    def __or__(self, other):
        """ORParameter syntax sugar"""
        return ORParameter(self, other)

    def raise_error(self, value, msg=""):
        """Raise InterfaceTypeError

        :param value: Value where error detected
        :type value: Arbitrary python type
        :param msg: Optional message
        :type msg: String
        :raises InterfaceTypeError
        """
        raise InterfaceTypeError("%s: %s. %s" % (self.__class__.__name__,
                                                 repr(value), msg))

    def clean(self, value):
        """
        Input parameter normalization

        :param value: Input parameter
        :type value: Arbitrary python type
        :return: Normalized value
        """
        return value

    def script_clean_input(self, profile, value):
        """
        Clean up script input parameters. Can be overloaded to
        handle profile specific.

        :param profile: Profile
        :type profile: Profile instance
        :param value: Input parameter
        :type value: Arbitrary python type
        :return: Normalized value
        """
        return self.clean(value)

    def script_clean_result(self, profile, value):
        """
        Clean up script result parameters. Can be overloaded to
        handle profile specific.

        :param profile: Profile
        :type profile: Profile instance
        :param value: Input parameter
        :type value: Arbitrary python type
        :return: Normalized value
        """
        return self.clean(value)

    def form_clean(self, value):
        """
        Clean up form field

        :param value: Input parameter
        :type value: Arbitrary python type
        :return: Normalized value
        """
        if not value and not self.required:
            return self.default if self.default else None
        try:
            return self.clean(value)
        except InterfaceTypeError as e:
            raise forms.ValidationError(e)

    def get_form_field(self, label=None):
        """
        Get appropriative form field
        """
        return {
            "xtype": "textfield",
            "name": label,
            "fieldLabel": label,
            "allowBlank": not self.required
        }


class ORParameter(BaseParameter):
    """
    >>> ORParameter(IntParameter(),IPv4Parameter()).clean(10)
    10
    >>> ORParameter(IntParameter(),IPv4Parameter()).clean("192.168.1.1")
    '192.168.1.1'
    >>> ORParameter(IntParameter(),IPv4Parameter()).clean("xxx") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    InterfaceTypeError: IPv4Parameter: 'xxx'
    >>> (IntParameter()|IPv4Parameter()).clean(10)
    10
    >>> (IntParameter()|IPv4Parameter()).clean("192.168.1.1")
    '192.168.1.1'
    >>> (IntParameter()|IPv4Parameter()).clean("xxx") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    InterfaceTypeError: IPv4Parameter: 'xxx'
    >>> (IntParameter()|IPv4Parameter()).clean(None) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    InterfaceTypeError: IPv4Parameter: None.
    >>> (IntParameter(required=False)|IPv4Parameter(required=False)).clean(None)
    >>> (IntParameter(required=False)|IPv4Parameter()).clean(None) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    InterfaceTypeError: IPv4Parameter: None.
    """
    def __init__(self, left, right):
        super(ORParameter, self).__init__()
        self.left = left
        self.right = right
        self.required = self.left.required or self.right.required

    def clean(self, value):
        if value is None and self.required == False:
            return None
        try:
            return self.left.clean(value)
        except InterfaceTypeError:
            return self.right.clean(value)

    def script_clean_input(self, profile, value):
        try:
            return self.left.script_clean_input(profile, value)
        except InterfaceTypeError:
            return self.right.script_clean_input(profile, value)

    def script_clean_result(self, profile, value):
        try:
            return self.left.script_clean_result(profile, value)
        except InterfaceTypeError:
            return self.right.script_clean_result(profile, value)
