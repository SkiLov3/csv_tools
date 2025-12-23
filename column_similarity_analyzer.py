import csv
import glob
import sys
import difflib
from collections import Counter

def analyze_similarity(filepath, column_name=None):
    print(f"\nAnalyzing {filepath}...")
    try:
        encoding = 'utf-8-sig' # Default to utf-8-sig to handle BOM
        try:
            with open(filepath, mode='r', newline='', encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                headers = reader.fieldnames
                rows = list(reader)
        except UnicodeDecodeError:
             encoding = 'cp1252' # Fallback
             with open(filepath, mode='r', newline='', encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                headers = reader.fieldnames
                rows = list(reader)

        if not headers:
            print("Error: CSV file seems valid but has no headers.")
            return

        # Column Selection Logic
        if not column_name or column_name not in headers:
            if column_name:
                print(f"Error: Column '{column_name}' not found in {filepath}.")
            
            print("\nAvailable columns:")
            for idx, col in enumerate(headers):
                print(f"{idx + 1}. {col}")

            while True:
                col_input = input("\nEnter column name or number: ").strip()
                if not col_input: continue
                if col_input.isdigit():
                    idx = int(col_input) - 1
                    if 0 <= idx < len(headers):
                        column_name = headers[idx]
                        break
                    else:
                        print(f"Number must be between 1 and {len(headers)}.")
                        continue
                found = False
                for col in headers:
                    if col.strip() == col_input:
                        column_name = col
                        found = True
                        break
                if found: break
                print("Column name not found or invalid number. Please try again.")

        print(f"Analyzing column: '{column_name}'")

        values = []
        for row in rows:
            val = row[column_name]
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
        # We will try to group "similar" values. 
        # Strategy: Sort by length/alpha to put similar items vaguely near? No, O(N^2) comparison is heavy.
        # But for typically small CSVs (<10k rows) and distinct values < 1k, it is fine.
        
        unique_vals = list(counts.keys())
        # Sort to make output deterministic and maybe help standard pairwise check
        unique_vals.sort()
        
        groups = []
        visited = set()
        
        # Threshold for similarity (0.0 to 1.0). 0.8 is usually decent for typos.
        cutoff = 0.6 

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
                
                # SequenceMatcher ratio
                # Quick check: if length difference is huge, skip
                if abs(len(root) - len(candidate)) > len(root) * (1-cutoff) + 2:
                     pass # optimization, maybe risky if very short strings
                
                ratio = difflib.SequenceMatcher(None, root.lower(), candidate.lower()).ratio()
                if ratio >= cutoff:
                    current_group.append((candidate, counts[candidate]))
                    visited.add(candidate)
            
            if len(current_group) > 1:
                groups.append(current_group)

        # Sort groups by total count of items in them
        groups.sort(key=lambda g: sum(x[1] for x in g), reverse=True)

        if not groups:
            print("No similar groups found.")
        else:
            for grp in groups:
                print("\nGroup:")
                total_in_chk = 0
                for val, count in grp:
                    print(f"  - '{val}' (Count: {count})")
                    total_in_chk += count
                print(f"  [Total in group: {total_in_chk}]")

    except Exception as e:
        print(f"Error reading {filepath}: {e}")

def main():
    csv_files = glob.glob('*.csv')
    if not csv_files:
        print("No CSV files found in the current directory.")
        return

    print("Found the following CSV files:")
    for i, f in enumerate(csv_files):
        print(f"{i+1}. {f}")
    
    while True:
        try:
            choice = input(f"\nEnter the number of the file to analyze (1-{len(csv_files)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(csv_files):
                target_file = csv_files[idx]
                break
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    column_name = None
    if len(sys.argv) > 1:
        column_name = sys.argv[1]
    
    analyze_similarity(target_file, column_name)

if __name__ == "__main__":
    main()
