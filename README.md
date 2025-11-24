# BixxyLogs 🎨

A colorful, category-based logging library for Python with emoji indicators and progress bars.

## Features

- 🎨 **Color-coded console output** with ANSI colors
- 📊 **Progress bar support** for long-running operations
- 📁 **Multi-level categorization** (name, category, subcategory)
- 📝 **File logging** with automatic rotation (keeps last 7 days)
- 🔔 **Multiple log levels**: DEBUG, INFO, SUCCESS, WARNING, ERROR
- 🎯 **Emoji indicators** for each log level

## Installation

### From GitHub
```bash
pip install git+https://github.com/ultimatemagenta/bixxylogs.git
```

### Local Development
```bash
git clone https://github.com/ultimatemagenta/bixxylogs.git
cd bixxylogs
pip install -e .
```

## Quick Start

```python
from bixxylogs import get_logger

# Create a logger
logger = get_logger(name="MyApp", category="Processing", subcategory="Files")

# Log messages
logger.info("Starting process...")
logger.success("Process completed!")
logger.warning("Low memory detected")
logger.error("Failed to connect")

# With progress bar
logger.info("Downloading...", percentage=45.5)
```

## Log Levels

| Level   | Icon | Color  | Description                    |
|---------|------|--------|--------------------------------|
| DEBUG   | 🐞   | Gray   | Detailed debug information     |
| INFO    | ℹ️   | Blue   | General informational messages |
| SUCCESS | ✅   | Green  | Success confirmations          |
| WARNING | ⚠️   | Yellow | Warning messages               |
| ERROR   | ❌   | Red    | Error messages                 |

## Console Output Format

```
2025-11-24 15:30:45 | ℹ️  | Processing | Files       | : Starting file scan...
2025-11-24 15:30:46 | ✅  | Processing | Files       | : 📁 ████████░░ [80.0%] - Processing...
```

## File Logging

Logs are automatically saved to `logs/` directory:
- By logger name: `logs/MyApp_2025-11-24.log`
- By category: `logs/Processing_2025-11-24.log`
- By subcategory: `logs/Processing/Files_2025-11-24.log`

Old log files (> 7 days) are automatically cleaned up.

## Advanced Usage

### Progress Bars
```python
logger = get_logger(name="Downloader")

for i in range(100):
    progress = (i + 1) / 100 * 100
    logger.info(f"Downloading file {i+1}/100", percentage=progress)
```

### Multiple Loggers
```python
main_logger = get_logger(name="MainApp")
db_logger = get_logger(name="MainApp", category="Database")
api_logger = get_logger(name="MainApp", category="API", subcategory="REST")
```

## License

MIT License - See LICENSE file for details

## Author

Created by ultimatemagenta
