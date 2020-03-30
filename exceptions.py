# Error codes constant
INVALID_DATA = "INVALID_DATA"
DUPLICATE_EMPLOYEE_ID = "DUPLICATE_EMPLOYEE_ID"
PARAM_MISSING = "PARAM_MISSING"
VALUE_MISSING = "VALUE_MISSING"
MISSING_INPUT_FILE = "MISSING_INPUT_FILE"
SOURCE_AND_DESTINATION_MATCHING = "SOURCE_AND_DESTINATION_MATCHING"


class Msgs(object):
    """ High Level class to print the error message"""

    class _Msg(object):
        """ Maintains a single printable message, error codes """

        def __init__(self, err_code, msg):
            self._err_code = err_code
            self._msg = msg

        def msg(self, *val):
            return self._apply_format_msg(self._msg, *val)

        @property
        def err(self):
            return self._err_code

        @staticmethod
        def _apply_format_msg(msg, *val):
            if not val:
                return msg
            elif isinstance(val, tuple):
                return str(msg).format(*val)
            return str(msg).format(val)

    msgs = {
        INVALID_DATA: _Msg("IE-1", "Input data given is invalid for Employee ID: {0}"),
        DUPLICATE_EMPLOYEE_ID: _Msg("IE-2", "Duplicate Employee ID given: '{0}'"),
        VALUE_MISSING: _Msg("IE-3", "Input request missing value. Please pass complete data:"
                                    "Employee: '{0}',  BuildingFrom: {1}, BuildingTo: {2}"),
        MISSING_INPUT_FILE: _Msg("IE-4", "Input file '{0}'is missing."),
        SOURCE_AND_DESTINATION_MATCHING: _Msg("IE-5", "Source Building and Destination Building are same,"
                                                      "Employee ID: '{0}', Building ID: {1}"),
        PARAM_MISSING: _Msg("IE-6", "Input 'request.csv' file contains wrong or missing Header Parameter."
                            "Parameter provided are {0}. Parameters should be: {1}"),

    }

    @classmethod
    def get_msg_err_code(cls, code, *value):
        _msg_obj = cls.msgs[code]
        if _msg_obj:
            return _msg_obj.err, _msg_obj.msg(*value)
        return ""


class GenericError(Exception):
    """Base class for other exceptions"""
    def __init__(self, error_code, *args):
        self.error_code, self.error_message = Msgs.get_msg_err_code(error_code, *args)
        super().__init__(self.error_message)

    def __str__(self):
        """ Return printable error message"""
        return "[{0}] {1}".format(self.error_code, self.error_message)


class InitializationError(GenericError):
    """ Fatal operation error. Stop and exit process"""
    pass
