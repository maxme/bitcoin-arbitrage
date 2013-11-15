import config, json, logging
from blinker import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

loaded = signal('config_loaded')
updated = signal('config_updated')
error = signal('config_error')

class ConfigEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory \
        and event.src_path.endswith("config.json"):
            update_config_from_json()
            updated.send(config)


def update_config_from_json():
    try:
        config_json = open("config.json", "r")

        for key, value in json.load(config_json).items():
            setattr(config, key, value)

        loaded.send(config)
    except ValueError as e:
        error.send(e)

def init():
    # Import config variables from JSON, if a config.json file exists.
    # If it does exist, watch it for changes. This will allow us to
    # change arbitrage configuration options without restarting the bot.
    try:
        update_config_from_json()
    except OSError:
        pass # No config.json? No problem.

handler = ConfigEventHandler()
observer = Observer()
observer.schedule(handler, ".")
observer.start()
