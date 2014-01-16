""" Allows for graceful degradation in the event that we can't load watchdog. """

class FileSystemEventHandler(object):
    pass

class Observer(object):
    def schedule(*args, **kwargs):
        pass

    def start(*args, **kwargs):
        pass
