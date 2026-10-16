import atexit
import datetime
import glob
import os
import re
import threading

from .console import print_log

LOG_LEVELS = {
    "DEBUG": {"icon": "🐞", "priority": 10},
    "INFO": {"icon": "ℹ️", "priority": 20},
    "SUCCESS": {"icon": "✅", "priority": 25},
    "WARNING": {"icon": "⚠️", "priority": 30},
    "ERROR": {"icon": "❌", "priority": 40},
}

# Réglages globaux. Rien n'est créé sur le disque tant qu'un message n'est pas écrit dans un fichier.
_config = {
    "log_dir": None,            # None = <dossier courant>/logs, résolu au premier message
    "console_level": "DEBUG",   # niveau minimal affiché à l'écran
    "file_level": "INFO",       # niveau minimal écrit dans les fichiers (DEBUG n'y va pas par défaut)
    "keep_days": 7,             # les fichiers plus vieux que N jours sont supprimés
    "files": True,              # False : écran seulement
}
_lock = threading.RLock()
_handles = {}                   # chemin de fichier -> fichier ouvert (partagé entre les loggers)
_cleaned = set()                # préfixes déjà nettoyés

_DATE_RE = re.compile(r"_(\d{4}-\d{2}-\d{2})\.log$")
_BAD_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def configure(log_dir=None, console_level=None, file_level=None, keep_days=None, files=None):
    """Règle le comportement global (appel facultatif)."""
    for key, value in (("log_dir", log_dir), ("console_level", console_level), ("file_level", file_level),
                       ("keep_days", keep_days), ("files", files)):
        if value is None:
            continue
        if key.endswith("_level"):
            value = str(value).upper()
            if value not in LOG_LEVELS:
                raise ValueError(f"Niveau inconnu : {value} (choix : {', '.join(LOG_LEVELS)})")
        with _lock:
            _config[key] = value


def _priority(level):
    return LOG_LEVELS[level]["priority"]


def _clean(value):
    return _BAD_CHARS.sub("_", str(value)).strip(" .") or "_"


def _log_dir():
    return _config["log_dir"] or os.path.join(os.getcwd(), "logs")


def _cleanup_old(prefix):
    """Supprime les fichiers <prefix>_AAAA-MM-JJ.log plus vieux que keep_days."""
    if prefix in _cleaned:
        return
    _cleaned.add(prefix)
    limit = datetime.date.today() - datetime.timedelta(days=int(_config["keep_days"]))
    for path in glob.glob(glob.escape(prefix) + "_*.log"):
        match = _DATE_RE.search(path)
        if not match:
            continue
        try:
            if datetime.date.fromisoformat(match.group(1)) < limit:
                os.remove(path)
        except (ValueError, OSError):
            pass


def _open(prefix):
    """Fichier du jour pour ce préfixe (ouvert une seule fois, même avec plusieurs loggers)."""
    path = f"{prefix}_{datetime.date.today():%Y-%m-%d}.log"
    handle = _handles.get(path)
    if handle is None or handle.closed:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        _cleanup_old(prefix)
        handle = open(path, "a", encoding="utf-8")
        _handles[path] = handle
    return handle


def close_all():
    """Ferme tous les fichiers de log (appelé automatiquement à la sortie du programme)."""
    with _lock:
        for handle in _handles.values():
            try:
                handle.close()
            except Exception:
                pass
        _handles.clear()


atexit.register(close_all)


class BixxyLogger:
    def __init__(self, name, category=None, subcategory=None):
        self.name = name
        self.category = category
        self.subcategory = subcategory

    def _prefixes(self):
        base = _log_dir()
        prefixes = []
        if self.name:
            prefixes.append(os.path.join(base, _clean(self.name)))
        if self.category:
            prefixes.append(os.path.join(base, _clean(self.category)))
        if self.subcategory:
            if self.category:
                prefixes.append(os.path.join(base, _clean(self.category), _clean(self.subcategory)))
            else:
                prefixes.append(os.path.join(base, _clean(self.subcategory)))
        return prefixes

    def _write(self, level, message, percentage=None, keep=False):
        priority = _priority(level)

        if priority >= _priority(_config["console_level"]):
            print_log(level, message, self.category, self.subcategory, percentage=percentage, keep=keep)

        if not _config["files"] or priority < _priority(_config["file_level"]):
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cat_str = f"[{self.category}]" if self.category else ""
        subcat_str = f"[{self.subcategory}]" if self.subcategory else ""
        pct_str = f" [{float(percentage):.1f}%]" if percentage is not None else ""
        log_line = f"[{timestamp}] [{level}] {cat_str} {subcat_str}{pct_str} {message}\n"

        with _lock:
            try:
                for prefix in self._prefixes():
                    handle = _open(prefix)
                    handle.write(log_line)
                    handle.flush()
            except OSError:
                pass  # un journal inaccessible ne doit jamais faire planter le programme

    # percentage : affiche une barre ; keep=True la garde à l'écran (sans keep, la ligne est écrasée par la suivante)
    def debug(self, msg, percentage=None, keep=False): self._write("DEBUG", msg, percentage, keep)
    def info(self, msg, percentage=None, keep=False): self._write("INFO", msg, percentage, keep)
    def success(self, msg, percentage=None, keep=False): self._write("SUCCESS", msg, percentage, keep)
    def warning(self, msg, percentage=None, keep=False): self._write("WARNING", msg, percentage, keep)
    def error(self, msg, percentage=None, keep=False): self._write("ERROR", msg, percentage, keep)


def get_logger(name="Default", category=None, subcategory=None):
    return BixxyLogger(name, category, subcategory)
