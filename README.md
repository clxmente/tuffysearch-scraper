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
uv run scrape.py
```

This will:
1. Create a virtual environment if it doesn't exist
2. Install dependencies from `pyproject.toml`
3. Fetch course data from the CSUF course catalog
4. Process and organize the information
5. Save the results to `data/raw_2025-2026_catalog.json`

### Process the raw data

To clean the data and extract relevant information, run the second script:
```bash
uv run reprocess.py
```

This will:
1. Read the JSON data taken from the scraped web pages
2. Save the processed data to `data/processed_2025-2026_catalog.json`
3. Print any unknown description blocks to the console

## 📁 Project Structure

```
tuffysearch-scraper/
├── data/                  # Output directory for JSON files
├── modules/              # Python modules
│   ├── course_departments.py  # Department mapping module
│   └── util.py          # Utility functions
├── models/              # Data models
│   └── courses.py       # Course data type definitions
├── scrape.py           # Main scraper script
├── reprocess.py        # Course data processing script
├── clean.py            # Unicode character cleaning utility
└── pyproject.toml      # Project metadata and dependencies
```

The project consists of two main scripts:

1. `scrape.py`: Scrapes course data from the CSUF course catalog using a multi-threaded approach with progress tracking
2. `reprocess.py`: Processes the raw course data into a structured format with progress tracking

The data flow is:
1. Raw course data is scraped and saved to `data/raw_YYYY-YYYY_catalog.json`
2. The raw data is processed and saved to `data/processed_YYYY-YYYY_catalog.json`

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
