#!/usr/bin/env python3
"""
Groups similar text entries in a column to identify typos, variations, or duplicates.
"""
import csv
import difflib
from collections import Counter
from utils import (
    select_file_interactive,
    select_column_interactive,
    read_csv_with_fallback_encoding,
    create_base_argparser
)


def analyze_similarity(filepath, column_name=None, cutoff=0.6):
    """
    Analyzes text similarity in a CSV column to find potential duplicates/typos.
    
    Args:
        filepath: Path to the CSV file
        column_name: Optional column name to analyze
        cutoff: Similarity threshold (0.0-1.0), default 0.6
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

    values = []
    for row in rows:
        val = row.get(column_name, '')
        if val and val.strip():
            values.append(val.strip())
    
    total_rows = len(rows)
    non_empty_count = len(values)
    
    print(f"Total Rows: {total_rows}")
    print(f"Non-empty Values: {non_empty_count}")

    # Exact Matches
    print("\n--- Top Exact Matches ---")
    counts = Counter(values)
    sorted_counts = counts.most_common(10)
    for val, count in sorted_counts:
        print(f"'{val}': {count}")

    # Similarity Grouping
    unique_vals = sorted(counts.keys())
    
    groups = []
    visited = set()

    print(f"\n--- Similarity Grouping (cutoff={cutoff}) ---")
    print("Grouping values that look similar (potential typos or variations)...")

    for i in range(len(unique_vals)):
        if unique_vals[i] in visited:
            continue
        
        root = unique_vals[i]
        current_group = [(root, counts[root])]
        visited.add(root)
        
        for j in range(i + 1, len(unique_vals)):
            candidate = unique_vals[j]
            if candidate in visited:
                continue
            
            # Length-based optimization: skip if lengths are too different
            len_diff = abs(len(root) - len(candidate))
            max_allowed_diff = len(root) * (1 - cutoff) + 2
            if len_diff > max_allowed_diff:
                continue
            
            ratio = difflib.SequenceMatcher(None, root.lower(), candidate.lower()).ratio()
            if ratio >= cutoff:
                current_group.append((candidate, counts[candidate]))
                visited.add(candidate)
        
        if len(current_group) > 1:
            groups.append(current_group)

    # Sort groups by total count
    groups.sort(key=lambda g: sum(x[1] for x in g), reverse=True)

    if not groups:
        print("No similar groups found.")
    else:
        for grp in groups:
            print("\nGroup:")
            total_in_grp = 0
            for val, count in grp:
                print(f"  - '{val}' (Count: {count})")
                total_in_grp += count
            print(f"  [Total in group: {total_in_grp}]")


def main():
    parser = create_base_argparser(
        "Group similar text entries in a column to identify typos and variations."
    )
    parser.add_argument(
        '--cutoff',
        type=float,
        default=0.8,
        help='Similarity threshold 0.0-1.0 (default: 0.8, higher = stricter matching)'
    )
    args = parser.parse_args()
    
    # Get file - from args or interactive
    target_file = args.file
    if not target_file:
        target_file = select_file_interactive()
        if not target_file:
            return
    
    analyze_similarity(target_file, args.column, args.cutoff)


if __name__ == "__main__":
    main()
