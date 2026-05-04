import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(('.py', '.js')):
            # Ignore node_modules, venv, and .git
            if any(x in event.src_path for x in ['node_modules', 'venv', '.git']):
                return
            
            logging.info(f"Detected change in: {event.src_path}")
            self.callback(event.src_path)

class FileWatcher:
    def __init__(self, watch_dir, callback):
        self.watch_dir = watch_dir
        self.callback = callback
        self.event_handler = CodeChangeHandler(self.callback)
        self.observer = Observer()

    def start(self):
        self.observer.schedule(self.event_handler, self.watch_dir, recursive=True)
        self.observer.start()
        logging.info(f"Started watching directory: {self.watch_dir}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    # Test run
    def test_callback(file_path):
        print(f"Callback triggered for {file_path}")

    watcher = FileWatcher(os.getcwd(), test_callback)
    watcher.start()
