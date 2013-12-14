import config, json, logging

# See if we can import blinker. If we can't, import our mock module instead.
try:
    from blinker import signal
    blinker_loaded = True

except ImportError:
    from mock_blinker import signal
    blinker_loaded = False

# See if we can import watchdog.
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    watchdog_loaded = True

except ImportError:
    from mock_watchdog import Observer, FileSystemEventHandler
    watchdog_loaded = False


class ConfigEventHandler(FileSystemEventHandler):
    """ A simple class for handling changes to config.json """

    def on_modified(self, event):
        if not event.is_directory \
        and event.src_path.decode("utf-8").endswith("config.json"):
            update_config_from_json()
            updated.send(config)


# Create our signals.
loaded = signal('config_loaded')
updated = signal('config_updated')
error = signal('config_error')

# Create and set up our event observers and handlers.
handler = ConfigEventHandler()
observer = Observer()
observer.schedule(handler, ".")
observer.start()


def update_config_from_json():
    # Loads config from config.json
    try:
        config_json = open("config.json", "r")

        for key, value in json.load(config_json).items():
            setattr(config, key, value)

        loaded.send(config)
    except ValueError as e:
        error.send(e)


def init():
    # Import config variables from JSON, if a config.json file exists.
    try:
        if not watchdog_loaded:
            logging.warn("Could not load 'watchdog'.")

        if not blinker_loaded:
            logging.warn("Could not load 'blinker'.")

        if not blinker_loaded or not watchdog_loaded:
            logging.warn("Dynamic config.json reloading disabled!")
            
        update_config_from_json()
    except OSError:
        pass # No config.json? No problem.


