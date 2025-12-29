# CSV Analysis Tools

This repository contains Python scripts for analyzing CSV data, specifically focused on registration and committee data.

## Scripts

### 1. `analyze_registrations_count.py`
**Purpose:** Analyzes product registrations from a sales/transaction CSV export.

**Features:**
- Interactive file and column selection.
- Parses cell data containing product details (Name, Quantity, Registration Type).
- Aggregates "Registration" products.
- Outputs total rows, total registrations, and a breakdown by registration type.
- Reports rows with content that didn't match expected patterns.

**Usage:**
```bash
python analyze_registrations_count.py [-f FILE] [-c COLUMN]
python analyze_registrations_count.py --help
```

### 2. `ypaa_comitee_analyzer.py`
**Purpose:** Normalizes and counts YPAA (Young People in Alcoholics Anonymous) committee names from survey or registration data.

**Features:**
- Interactive file and column selection.
- **Normalization:** Converts variations and typos (e.g., "SALTYPAA", "sltypaa") to standardized canonical names (e.g., "UCYPAA").
- **Smart Extraction:** Handles multiple committees in a single field (split by `/`, `&`, `and`, etc.).
- **Filtering:** Ignores "No", "Not Applicable", and vague "Yes" responses.
- **Reporting:** Displays a ranked list of committees mentioned N or more times (configurable), along with stats on unspecific or filtered responses.

**Usage:**
```bash
python ypaa_comitee_analyzer.py [-f FILE] [-c COLUMN] [-p PRODUCTS_COLUMN] [-t THRESHOLD]
python ypaa_comitee_analyzer.py --help
```

### 3. `column_similarity_analyzer.py`
**Purpose:** Groups similar text entries in a column to identify typos, variations, or duplicates using fuzzy matching.

**Features:**
- Interactive file and column selection.
- **Similarity Grouping:** Uses standard library `difflib` to group values that are textually similar (e.g., "Vegetarian" and "Vegetarian option").
- **Configurable cutoff:** Adjust similarity threshold via `--cutoff` (default: 0.6).
- **Reporting:** Shows top exact matches and clusters of similar values.

**Usage:**
```bash
python column_similarity_analyzer.py [-f FILE] [-c COLUMN] [--cutoff CUTOFF]
python column_similarity_analyzer.py --help
```

### 4. `utils.py`
**Purpose:** Shared utilities used by all scripts.

**Features:**
- Common file/column selection logic
- CSV reading with encoding fallback (utf-8-sig, utf-8, cp1252, latin-1)
- Base argparse configuration

## Requirements
- Python 3.7+
- Standard libraries: `csv`, `re`, `glob`, `sys`, `argparse`, `collections`, `difflib`
