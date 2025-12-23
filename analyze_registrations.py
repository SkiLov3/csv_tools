import csv
import glob
import sys
import os
import re

def analyze_csv(filepath, column_name=None):
    print(f"\nAnalyzing {filepath}...")
    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames
            
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
                    
                    if not col_input:
                        continue

                    # Try parsing as integer index
                    if col_input.isdigit():
                        idx = int(col_input) - 1
                        if 0 <= idx < len(headers):
                            column_name = headers[idx]
                            break
                        else:
                            print(f"Number must be between 1 and {len(headers)}.")
                            continue
                    
                    # Try matching column name
                    found = False
                    for col in headers:
                        if col.strip() == col_input:
                            column_name = col
                            found = True
                            break
                    
                    if found:
                        break
                    
                    print("Column name not found or invalid number. Please try again.")

            print(f"Analyzing column: '{column_name}'")

            total_rows = 0
            total_registrations = 0
            breakdown = {}
            
            # Regex to match: "Product Name (Amount: ..., Quantity: N, ...)"
            # Handling potential multiline complexity where one cell has multiple products
            product_pattern = re.compile(r'(.*?)\s*\(Amount:.*?, Quantity:\s*(\d+)(?:, Registration Type:\s*(.*?))?.*?\)')

            for row in reader:
                total_rows += 1
                cell_value = row[column_name]
                if not cell_value:
                    continue
                
                # Split by newlines as sometimes multiple products are in one cell
                lines = cell_value.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("Total:") or line.startswith("Transaction ID:"):
                        continue
                        
                    match = product_pattern.search(line)
                    if match:
                        name = match.group(1).strip()
                        quantity = int(match.group(2))
                        reg_type = match.group(3).strip() if match.group(3) else "Unspecified"
                        
                        # We only want to count things that look like Registrations
                        # Adjust this filter as needed based on specific requirements, 
                        # but usually "Registration" is in the name.
                        # If the user wants ALL items counted, we can remove the filter.
                        # Based on "count of registrations", I'll check for "Registration" in name.
                        if "Registration" in name:
                            total_registrations += quantity
                            
                            key = f"{name} - {reg_type}"
                            breakdown[key] = breakdown.get(key, 0) + quantity

            print(f"Total rows processed: {total_rows}")
            print(f"Total Registrations Counted: {total_registrations}")
            print("\nBreakdown by Type:")
            for key, count in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
                print(f"  {key}: {count}")
                
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

    # Check for command line arg for column name
    column_name = None
    if len(sys.argv) > 1:
        column_name = sys.argv[1]
    
    # We pass column_name (None or from argv) to analyze_csv
    # It will handle asking the user if it's None.
    analyze_csv(target_file, column_name)

if __name__ == "__main__":
    main()
