
class ArgumentTypeException(Exception):
    def __init__(self, error_msg):
        Exception.__init__(self, error_msg)

class LengthTooLongException(Exception):
    def __init__(self, error_msg):
        Exception.__init__(self, error_msg)
        # TODO: should have a log here

class CustomListException(Exception):
    def __init__(self, element, clazz):
        Exception.__init__(self, "Element[%s] type error, each element should be [%s]" %
                           (element, clazz))

