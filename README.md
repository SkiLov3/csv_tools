# CSV Analysis Tools

This repository contains Python scripts for analyzing CSV data, specifically focused on registration and committee data.

## Scripts

### 1. `analyze_registrations.py`
**Purpose:** Analyzes product registrations from a sales/transaction CSV export.

**Features:**
- Interactive file and column selection.
- Parses cell data containing product details (Name, Quantity, Registration Type).
- Aggregates "Registration" products.
- Outputs total rows, total registrations, and a breakdown by registration type.

**Usage:**
```bash
python analyze_registrations.py [optional_column_name]
```

### 2. `ypaa_comitee_analyzer.py`
**Purpose:** Normalizes and counts YPAA (Young People in Alcoholics Anonymous) committee names from survey or registration data.

**Features:**
- Interactive file and column selection.
- **Normalization:** Converts variations and typos (e.g., "SALTYPAA", "sltypaa") to standardized canonical names (e.g., "UCYPAA").
- **Smart Extraction:** Handles multiple committees in a single field (split by `/`, `&`, `and`, etc.).
- **Filtering:** Ignores "No", "Not Applicable", and vague "Yes" responses.
- **Reporting:** Displays a ranked list of committees mentioned 2 or more times, along with stats on unspecific or filtered responses.

**Usage:**
```bash
python ypaa_comitee_analyzer.py
```

### 3. `column_similarity_analyzer.py`
**Purpose:** Groups similar text entries in a column to identify typos, variations, or duplicates using fuzzy matching.

**Features:**
- Interactive file and column selection.
- **Similarity Grouping:** Uses standard library `difflib` to group values that are textually similar (e.g., "Vegetarian" and "Vegetarian option").
- **Reporting:** Shows top exact matches and clusters of similar values.

**Usage:**
```bash
python column_similarity_analyzer.py [optional_column_name]
```

## Requirements
- Python 3.x
- Standard libraries: `csv`, `re`, `glob`, `sys`, `os`, `collections`, `difflib`
