import os
import datetime
import glob
from .console import print_log  # on l'ajoutera dans l'étape suivante

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_LEVELS = {
    "DEBUG": {"icon": "🐞", "priority": 10},
    "INFO": {"icon": "ℹ️", "priority": 20},
    "SUCCESS": {"icon": "✅", "priority": 25},
    "WARNING": {"icon": "⚠️", "priority": 30},
    "ERROR": {"icon": "❌", "priority": 40},
}

class BixxyLogger:
    def __init__(self, name, category=None, subcategory=None):
        self.name = name
        self.category = category
        self.subcategory = subcategory

        self.files = {}
        self._init_log_files()

    def _init_log_files(self):
        for level in ["name", "category", "subcategory"]:
            value = getattr(self, level)
            if value:
                path = os.path.join(LOG_DIR, f"{value}.log")
                self.files[level] = open(path, "a", encoding="utf-8")

    def _open_log_files(self):
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")

        def open_and_clean_log(path_base, key):
            pattern = f"{path_base}_*.log"
            files = sorted(glob.glob(pattern))
            if len(files) > 7:
                for old_file in files[:-7]:
                    try:
                        os.remove(old_file)
                    except Exception:
                        pass

            log_file = f"{path_base}_{today_str}.log"
            self.files[key] = open(log_file, "a", encoding="utf-8")

        # 1. log file by name
        if self.name:
            open_and_clean_log(os.path.join(log_dir, self.name), "name")

        # 2. log file by category
        if self.category:
            open_and_clean_log(os.path.join(log_dir, self.category), "category")

        # 3. log file by subcategory
        if self.category and self.subcategory:
            sub_dir = os.path.join(log_dir, self.category)
            os.makedirs(sub_dir, exist_ok=True)
            open_and_clean_log(os.path.join(sub_dir, self.subcategory), "subcategory")

    def _write(self, level, message, percentage=None):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cat_str = f"[{self.category}]" if self.category else ""
        subcat_str = f"[{self.subcategory}]" if self.subcategory else ""
        log_line = f"[{timestamp}] [{level}] {cat_str} {subcat_str} {message}\n"

        # Console output
        print_log(level, message, self.category, self.subcategory, percentage=percentage)

        if level == "DEBUG":
            return

        for file in self.files.values():
            file.write(log_line)
            file.flush()

    def debug(self, msg, percentage=None): self._write("DEBUG", msg, percentage)
    def info(self, msg, percentage=None): self._write("INFO", msg, percentage)
    def success(self, msg, percentage=None): self._write("SUCCESS", msg, percentage)
    def warning(self, msg, percentage=None): self._write("WARNING", msg, percentage)
    def error(self, msg, percentage=None): self._write("ERROR", msg, percentage)

def get_logger(name="Default", category=None, subcategory=None):
    return BixxyLogger(name, category, subcategory)
