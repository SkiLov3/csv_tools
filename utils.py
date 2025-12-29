"""
Shared utilities for CSV analysis tools.
"""
import csv
import glob
import argparse


def select_file_interactive():
    """
    Interactively prompts the user to select a CSV file from the current directory.
    Returns the selected filename or None if no files found.
    """
    csv_files = glob.glob('*.csv')
    if not csv_files:
        print("No CSV files found in the current directory.")
        return None

    print("Found the following CSV files:")
    for i, f in enumerate(csv_files):
        print(f"{i+1}. {f}")
    
    while True:
        try:
            choice = input(f"\nEnter the number of the file to analyze (1-{len(csv_files)}): ").strip()
            if not choice:
                continue
            idx = int(choice) - 1
            if 0 <= idx < len(csv_files):
                return csv_files[idx]
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def select_column_interactive(headers, column_name=None, default_index=None, prompt_suffix=""):
    """
    Interactively prompts the user to select a column from the given headers.
    
    Args:
        headers: List of column names
        column_name: Optional pre-specified column name to use if valid
        default_index: Optional default column index (0-indexed) if user presses Enter
        prompt_suffix: Additional text to append to the prompt
    
    Returns:
        The selected column name
    """
    # If column_name provided and exists, use it
    if column_name and column_name in headers:
        return column_name
    
    if column_name:
        print(f"Error: Column '{column_name}' not found.")
    
    print("\nAvailable columns:")
    for idx, col in enumerate(headers):
        print(f"{idx + 1}. {col}")

    default_msg = ""
    if default_index is not None and 0 <= default_index < len(headers):
        default_msg = f" (default {default_index + 1})"

    while True:
        col_input = input(f"\nEnter column name or number{default_msg}{prompt_suffix}: ").strip()
        
        # Handle default
        if not col_input:
            if default_index is not None and 0 <= default_index < len(headers):
                return headers[default_index]
            continue

        # Try parsing as integer index
        if col_input.isdigit():
            idx = int(col_input) - 1
            if 0 <= idx < len(headers):
                return headers[idx]
            else:
                print(f"Number must be between 1 and {len(headers)}.")
                continue
        
        # Try matching column name
        for col in headers:
            if col.strip() == col_input:
                return col
        
        print("Column name not found or invalid number. Please try again.")


def read_csv_with_fallback_encoding(filepath, use_dictreader=True):
    """
    Reads a CSV file with encoding fallback (tries utf-8-sig, then cp1252).
    
    Args:
        filepath: Path to the CSV file
        use_dictreader: If True, returns (headers, rows) using DictReader
                       If False, returns (header_list, row_lists) using reader
    
    Returns:
        Tuple of (headers, rows)
    
    Raises:
        FileNotFoundError: If file doesn't exist
        csv.Error: If CSV parsing fails
    """
    encodings = ['utf-8-sig', 'utf-8', 'cp1252', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(filepath, mode='r', newline='', encoding=encoding) as csvfile:
                if use_dictreader:
                    reader = csv.DictReader(csvfile)
                    headers = reader.fieldnames
                    rows = list(reader)
                else:
                    reader = csv.reader(csvfile)
                    headers = next(reader)
                    rows = list(reader)
                return headers, rows
        except UnicodeDecodeError:
            continue
    
    raise UnicodeDecodeError(f"Could not decode file with any of: {encodings}")


def create_base_argparser(description):
    """
    Creates a base argument parser with common arguments for CSV tools.
    
    Args:
        description: Description for the script
    
    Returns:
        argparse.ArgumentParser with --file and --column arguments
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '-f', '--file',
        help='Path to the CSV file to analyze (interactive selection if not provided)'
    )
    parser.add_argument(
        '-c', '--column',
        help='Name of the column to analyze (interactive selection if not provided)'
    )
    return parser
