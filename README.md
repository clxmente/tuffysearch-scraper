# TuffySearch Course Catalog Scraper

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A multi-threaded web scraper for the Cal State Fullerton course catalog. This tool fetches course information including titles, descriptions, departments, and units from the university's course catalog website.

## 🚀 Features

- Multi-threaded scraping for improved performance
- Progress tracking with rich console output
- Automatic handling of course departments from section headers
- Unicode character cleaning utility
- JSON output format for easy data processing

## 📋 Prerequisites

- Python 3.12 or higher
- `uv` package manager

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tuffysearch-scraper.git
cd tuffysearch-scraper
```

2. Install `uv` if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 🏃‍♂️ Usage

### Scraping the Course Catalog

Simply run:
```bash
uv run main.py
```

This will:
1. Create a virtual environment if it doesn't exist
2. Install dependencies from `pyproject.toml`
3. Fetch course data from the CSUF course catalog
4. Process and organize the information
5. Save the results to `data/2025-2026_catalog.json`

### Cleaning Unicode Characters

To clean unicode escape sequences from the course descriptions:
```bash
uv run clean.py
```

This will:
1. Read the catalog JSON file
2. Replace special characters with their ASCII equivalents
3. Save the cleaned data to a new file
4. Print any unknown characters that weren't in the translation map

## 📁 Project Structure

```
tuffysearch-scraper/
├── data/                  # Output directory for JSON files
├── modules/              # Python modules
│   └── course_departments.py  # (Legacy) Department mapping module
├── main.py              # Main scraper script
├── clean.py             # Unicode character cleaning utility
└── pyproject.toml       # Project metadata and dependencies
```

## 🔧 Technical Details

- Uses `requests` for HTTP requests
- `BeautifulSoup4` for HTML parsing
- `rich` for beautiful console output
- Multi-threading with `ThreadPoolExecutor`
- Progress tracking with custom progress bars

## 📝 Notes

- The scraper is configured for the 2025-2026 course catalog
- Course departments are now extracted from section headers instead of the department mapping page
- The `course_departments.py` module is currently unused but kept for reference
- Uses modern Python packaging with `pyproject.toml`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
