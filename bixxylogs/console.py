import os
import sys
import threading
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

# ANSI colors
COLORS = {
    "DEBUG": "\033[90m",         # gris
    "INFO": "\033[94m",          # bleu
    "SUCCESS": "\033[92m",       # vert
    "WARNING": "\033[93m",       # jaune
    "ERROR": "\033[91m",         # rouge
    "CATEGORY": "\033[34m",      # bleu foncé
    "SUBCATEGORY": "\033[36m",   # bleu clair
    "MESSAGE": "\033[97m",       # blanc
    "RESET": "\033[0m"
}

FIELD_WIDTHS = {
    "CATEGORY": 10,
    "SUBCATEGORY": 12
}

SYMBOLS = {
    "DEBUG": "🐞",
    "INFO": "ℹ️",
    "SUCCESS": "✅",
    "WARNING": "⚠️",
    "ERROR": "❌",
}
# Repli quand la console ne sait pas encoder les emojis (ex. cp1252 sous Windows)
ASCII_SYMBOLS = {
    "DEBUG": "[D]",
    "INFO": "[i]",
    "SUCCESS": "[+]",
    "WARNING": "[!]",
    "ERROR": "[x]",
}

_last_was_inline = False
_lock = threading.RLock()
_ansi_ready = False


def _enable_ansi():
    """Active les séquences ANSI dans la console Windows (une seule fois)."""
    global _ansi_ready
    if _ansi_ready:
        return
    _ansi_ready = True
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass


def _use_color():
    return "NO_COLOR" not in os.environ


def _encoding():
    return getattr(sys.stdout, "encoding", None) or "utf-8"


def _can_encode(text):
    try:
        text.encode(_encoding())
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def _safe(text):
    """Remplace ce que la console ne sait pas afficher au lieu de lever UnicodeEncodeError."""
    enc = _encoding()
    try:
        return text.encode(enc, "replace").decode(enc, "replace")
    except LookupError:
        return text


def format_field(value, length):
    value = str(value) if value else "-"
    if len(value) > length:
        return value[:length]
    return value.ljust(length)


def LOG_SYMBOL(level):
    if _can_encode("".join(SYMBOLS.values()) + "█░📁"):
        return SYMBOLS.get(level, "❔")
    return ASCII_SYMBOLS.get(level, "[?]")


def print_log(level, message, category=None, subcategory=None, overwrite=False, percentage=None, keep=False):
    global _last_was_inline

    _enable_ansi()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colors = COLORS if _use_color() else {k: "" for k in COLORS}
    color = colors.get(level, colors["RESET"])
    reset = colors["RESET"]

    symbol = LOG_SYMBOL(level)
    unicode_ok = symbol in SYMBOLS.values()
    cat_str = format_field(category, FIELD_WIDTHS["CATEGORY"])
    subcat_str = format_field(subcategory, FIELD_WIDTHS["SUBCATEGORY"])

    # Couleur du message selon le niveau
    if level in ["ERROR", "WARNING"]:
        msg_color = colors[level]
    else:
        msg_color = colors["MESSAGE"]
    # Barre de progression si pourcentage donné
    bar = ""
    if percentage is not None:
        try:
            percent = float(percentage)
            percent = max(0, min(100, percent))  # Clamp
            filled = int(percent // 10)
            empty = 10 - filled
            if unicode_ok:
                bar = f"📁 {'█' * filled}{'░' * empty} [{percent:.1f}%] - "
            else:
                bar = f"{'#' * filled}{'.' * empty} [{percent:.1f}%] - "
            overwrite = not keep  # keep=True : la barre reste affichée, la ligne n'est pas écrasée
        except ValueError:
            bar = ""

    formatted = _safe(
        f"{color}{now}{reset} | "
        f"{color}{symbol}{reset} | "
        f"{colors['CATEGORY']}{cat_str}{reset} | "
        f"{colors['SUBCATEGORY']}{subcat_str}{reset} | : "
        f"{msg_color}{bar}{message}{reset}"
    )

    end_char = "\r" if overwrite else "\n"
    with _lock:
        if overwrite:
            # Efface proprement la ligne précédente avant de réécrire
            sys.stdout.write("\r" + " " * 200 + "\r")
            _last_was_inline = True
        elif _last_was_inline:
            sys.stdout.write("\r" + " " * 200 + "\r")
            _last_was_inline = False

        sys.stdout.write(formatted + end_char)
        sys.stdout.flush()
