import sys
from datetime import datetime
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

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

_last_was_inline = False

def format_field(value, length):
    value = str(value) if value else "-"
    if len(value) > length:
        return value[:length]
    return value.ljust(length)

def print_log(level, message, category=None, subcategory=None, overwrite=False, percentage=None):
    global _last_was_inline

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = COLORS.get(level, COLORS["RESET"])
    reset = COLORS["RESET"]

    symbol = LOG_SYMBOL(level)
    cat_str = format_field(category, FIELD_WIDTHS["CATEGORY"])
    subcat_str = format_field(subcategory, FIELD_WIDTHS["SUBCATEGORY"])

    # Couleur du message selon le niveau
    if level in ["ERROR", "WARNING"]:
        msg_color = COLORS[level]
    else:
        msg_color = COLORS["MESSAGE"]
    # Barre de progression si pourcentage donné
    bar = ""
    if percentage is not None:
        try:
            percent = float(percentage)
            percent = max(0, min(100, percent))  # Clamp
            filled = int(percent // 10)
            empty = 10 - filled
            bar = f"📁 {'█' * filled}{'░' * empty} [{percent:.1f}%] - "
            overwrite = True
        except ValueError:
            bar = ""

    formatted = (
        f"{color}{now}{reset} | "
        f"{color}{symbol}{reset} | "
        f"{COLORS['CATEGORY']}{cat_str}{reset} | "
        f"{COLORS['SUBCATEGORY']}{subcat_str}{reset} | : "
        f"{msg_color}{bar}{message}{reset}"
    )

    end_char = "\r" if overwrite else "\n"
    if overwrite:
        # Efface proprement la ligne précédente avant de réécrire
        sys.stdout.write("\r" + " " * 200 + "\r")
        _last_was_inline = True
    else:
        if _last_was_inline:
            sys.stdout.write("\r" + " " * 200 + "\r")
            _last_was_inline = False


    sys.stdout.write(formatted + end_char)
    sys.stdout.flush()


def LOG_SYMBOL(level):
    return {
        "DEBUG": "🐞",
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
    }.get(level, "❔")
