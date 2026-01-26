#!/usr/bin/env python3
"""
Analyzes product registrations from a sales/transaction CSV export.
"""
import csv
import re
from utils import (
    select_file_interactive,
    select_column_interactive,
    read_csv_with_fallback_encoding,
    create_base_argparser
)


def analyze_csv(filepath, column_name=None):
    """
    Analyzes registration data from a CSV file.
    
    Args:
        filepath: Path to the CSV file
        column_name: Optional column name to analyze
    """
    print(f"\nAnalyzing {filepath}...")
    
    try:
        headers, rows = read_csv_with_fallback_encoding(filepath, use_dictreader=True)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return
    except UnicodeDecodeError as e:
        print(f"Error: Could not decode file - {e}")
        return
    except csv.Error as e:
        print(f"Error: CSV parsing failed - {e}")
        return
    
    if not headers:
        print("Error: CSV file seems valid but has no headers.")
        return

    # Column Selection
    column_name = select_column_interactive(headers, column_name)
    print(f"Analyzing column: '{column_name}'")

    total_rows = 0
    total_registrations = 0
    breakdown = {}
    rows_without_matches = 0
    
    # Regex to match: "Product Name (Amount: XX.XX USD, Quantity: N, ...)"
    product_pattern = re.compile(
        r'(.*?)\s*\(Amount:\s*([\d\.]+).*?, Quantity:\s*(\d+)(?:, Registration Type:\s*([^,)]+))?.*?\)'
    )

    price_counts = {0: 0, 20: 0, 25: 0, 30: 0, 35: 0, 40: 0, 50: 0}
    other_price_counts = {}

    for row in rows:
        total_rows += 1
        cell_value = row.get(column_name, '')
        if not cell_value:
            continue
        
        # Split by newlines as sometimes multiple products are in one cell
        lines = cell_value.split('\n')
        found_match = False
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("Total:") or line.startswith("Transaction ID:"):
                continue
                
            match = product_pattern.search(line)
            if match:
                found_match = True
                name = match.group(1).strip()
                try:
                    price_val = float(match.group(2))
                    # Treat 20.00 as 20
                    if price_val.is_integer():
                        price_val = int(price_val)
                except ValueError:
                    price_val = 0

                quantity = int(match.group(3))
                reg_type = match.group(4).strip() if match.group(4) else "Unspecified"
                
                # Only count items that look like Registrations
                if "Registration" in name:
                    total_registrations += quantity
                    key = f"{name} - {reg_type}"
                    breakdown[key] = breakdown.get(key, 0) + quantity

                    # Track by price
                    if price_val in price_counts:
                        price_counts[price_val] += quantity
                    else:
                        other_price_counts[price_val] = other_price_counts.get(price_val, 0) + quantity
        
        # Track rows with non-empty content but no pattern matches
        if cell_value.strip() and not found_match:
            rows_without_matches += 1

    print(f"\nTotal rows processed: {total_rows}")
    print(f"Total Registrations Counted: {total_registrations}")
    
    if rows_without_matches > 0:
        print(f"Rows with content but no pattern matches: {rows_without_matches}")
    
    print("\nRegistrations by Price Point:")
    for price in [0, 20, 25, 30, 35, 40, 50]:
        count = price_counts.get(price, 0)
        print(f"  ${price}: {count}")
    
    if other_price_counts:
        print("  Other Prices:")
        for price, count in sorted(other_price_counts.items()):
            print(f"    ${price}: {count}")

    print("\nBreakdown by Type:")
    for key, count in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
        print(f"  {key}: {count}")


def main():
    parser = create_base_argparser(
        "Analyze product registrations from a sales/transaction CSV export."
    )
    args = parser.parse_args()
    
    # Get file - from args or interactive
    target_file = args.file
    if not target_file:
        target_file = select_file_interactive()
        if not target_file:
            return
    
    analyze_csv(target_file, args.column)


if __name__ == "__main__":
    main()
