""" Allows for graceful degradation when 'blinker' is not installed. """

class MockSignal(object):
    def connect(*args, **kwargs):
        pass

    def send(*args, **kwargs):
        pass


def signal(*args, **kwargs):
    return MockSignal()
