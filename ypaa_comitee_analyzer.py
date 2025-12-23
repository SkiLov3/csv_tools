import csv
import re
import glob
import sys
import os
from collections import Counter

def extract_groups(name):
    """
    Extracts a list of standardized committee/group names from a string.
    Handles multiple groups (separated by /, &, and, ,) and typos.
    """
    if not name or not name.strip():
        return ['Not Specified / Not a YPAA']
        
    name_lower = name.strip().lower()

    # Standardize 'No' / 'Not Specified' answers
    no_responses = {
        '', 'nan', 'no', 'nope', 'not yet', 'not right now', 'maybe', 
        'not currently', 'not at this time', 'hell no', 'naur', 'n', 
        'not yet!', 'not this year', 'there isnt one near me :(', 
        'negative/supporter/cheerleader'
    }
    
    if name_lower in no_responses:
        return ['Not Specified / Not a YPAA']

    # Handle explicit "Yes" but no content
    if name_lower in ['yes', 'why yes i am', 'yes .', 'yea', 'yes!']:
         return ['Yes, Unspecified Group']

    # Splitting logic remains same
    
    # Normalization map for canonical names
    normalization_map = {
        'SALTYPAA': 'UCYPAA',
        'SLUTYPAA': 'UCYPAA',
        'SLTYPAA': 'UCYPAA'
    }

    # Known typos map
    # Maps lowercase variations/typos/abbreviations to the correct Standardized YPAA Name
    typos = {
        'ucpaa': 'UCYPAA',
        'sltypaa': 'UCYPAA', # Was SALTYPAA, now normalizing to UCYPAA
        'buttey': 'BUTTEYPAA',
        'wac': 'WACYPAA',
        'wacy': 'WACYPAA',
        'sacy': 'SACYPAA',
        'renvy': 'RENVYPAA',
        'renypaa': 'RENVYPAA',
        'swac': 'SWACYPAA', # might catch swac xi
        'swacypa': 'SWACYPAA',
        'burquypaa': 'BURQYPAA',
        'burqypqaa': 'BURQYPAA',
        'nacypa': 'NACYPAA',
        'ccpaa': 'CCYPAA',
        'bellypa': 'BELLYPAA',
        'bacy': 'BACYPAA', # catch bacy paa
        'tity': 'TITYPAA'
    }

    # Split into potential group chunks
    # Split by forward slash, ampersand, comma, ' and ', ' & '
    parts = re.split(r'[/,&]|\s+and\s+', name)
    
    found_groups = []
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        part_lower = part.lower()
        
        # Check explicit typos/mappings first
        # We check if the part *contains* the typo word or IS the typo word
        # But 'sltypaa' is solid. 'Ucpaa' might be 'Ucpaa something'. 
        # Simple exact match or simple containment for the typo?
        # Let's clean the part to just alpha chars for checking typos maybe?
        # Or just use the regex.
        
        # Regex for YPAA
        match = re.search(r'\b([a-zA-Z]*YPAA)\b', part, re.IGNORECASE)
        if match:
            found_name = match.group(1).upper()
            # Normalize if needed
            if found_name in normalization_map:
                found_name = normalization_map[found_name]
            found_groups.append(found_name)
            continue
            
        # Check typos map if regex failed
        # If the part contains 'ucpaa', map it.
        for typo, correction in typos.items():
            if typo in part_lower:
                found_groups.append(correction)
                break
        else:
            # If loop finished without break (no typo found)
            # If it has "Host" or "Advisory", only add if we haven't found other groups?
            # Or treat as "Host/Advisory" group.
            if 'host' in part_lower or 'advisory' in part_lower:
                # If we already found a YPAA in this part (via regex), we wouldn't be here.
                # But maybe the part is "WACYPAA Host". Regex caught WACYPAA.
                # If part is just "Host", we want to capture that.
                if not found_groups: # Only fallback if nothing else found? 
                    # Warning: this logic operates per-part.
                    # If input is "WACYPAA Host", part is "WACYPAA Host". Regex finds WACYPAA.
                    # If input is "Host", part is "Host". regex fails. typos fail.
                    found_groups.append('Host / Advisory (Unspecified YPAA)')
                pass
            
    if found_groups:
        return list(set(found_groups)) # Unique per line
        
    # If we processed all parts and found nothing specific, but it wasn't a "No":
    # Fallback to Title Case of the whole string if short, or categorize as Unspecified?
    # Original logic: return name.title()
    # But now we might have broken it up. 
    # Let's just return Title Case of the cleaned original if reasonable, or 'Other'
    
    # If it contains "Yes" or similar but we missed it above
    if 'yes' in name_lower:
         return ['Yes, Unspecified Group']
         
    return [name.strip().title()]


def select_file():
    csv_files = glob.glob('*.csv')
    if not csv_files:
        print("No CSV files found in the current directory.")
        return None

    print("Found the following CSV files:")
    for i, f in enumerate(csv_files):
        print(f"{i+1}. {f}")
    
    while True:
        try:
            col_input = input(f"\nEnter the number of the file to analyze (1-{len(csv_files)}): ").strip()
            # Default to 1 if empty? No, better explicit.
            if not col_input:
                continue
                
            idx = int(col_input) - 1
            if 0 <= idx < len(csv_files):
                return csv_files[idx]
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    print("--- YPAA Committee Analyzer ---")
    file_path = select_file()
    if not file_path:
        return

    print(f"\nLoading {file_path}...")
    try:
        # Use simple latin-1 or similar if cp1252 was dealing with weird chars; 
        # python's 'utf-8-sig' or 'latin-1' usually behaves well. original used 'cp1252'.
        # We'll try utf-8 first, fallback to cp1252 if needed.
        encoding = 'cp1252' 
        
        rows = []
        try:
            with open(file_path, mode='r', newline='', encoding=encoding) as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)
                rows = list(reader)
        except UnicodeDecodeError:
             with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)
                rows = list(reader)

        # Display available columns
        print("\nAvailable columns:")
        for idx, col in enumerate(header):
            print(f"{idx + 1}. {col}")

        while True:
            col_input = input("\nEnter column name or number (default 5): ").strip()
            
            # Default to 5th column (index 4) if empty, for backward compatibility/ease
            if not col_input:
                column_index = 4
                if column_index < len(header):
                    break
                else:
                    print("Default column index 4 out of range.")
                    continue

            # Try parsing as integer index
            if col_input.isdigit():
                idx = int(col_input) - 1
                if 0 <= idx < len(header):
                    column_index = idx
                    break
                else:
                    print(f"Number must be between 1 and {len(header)}.")
                    continue
            
            # Try matching column name
            found = False
            for idx, col in enumerate(header):
                if col.strip() == col_input:
                    column_index = idx
                    found = True
                    break
            
            if found:
                break
            
            print("Column name not found or invalid number. Please try again.")

        column_name = header[column_index]
        print(f"Analyzing column: '{column_name}'")
        
        all_groups = []
        for row in rows:
            if len(row) > column_index:
                val = row[column_index]
                groups = extract_groups(val)
                all_groups.extend(groups)
            else:
                all_groups.append('Not Specified / Not a YPAA') # Handle short rows
        
        # Calculate counts
        group_counts = Counter(all_groups)
        
        # Filter logic
        threshold = 2
        
        filtered_items = []
        dissimilar_sum = 0
        no_specified_sum = 0
        yes_unspecified_sum = 0
        total_mentions = 0
        
        for group, count in group_counts.items():
            total_mentions += count
            
            if group == 'Not Specified / Not a YPAA':
                no_specified_sum += count
            elif group == 'Yes, Unspecified Group':
                yes_unspecified_sum += count
            elif count == 1:
                dissimilar_sum += count
            elif count >= threshold:
                filtered_items.append((group, count))
                
        # Sort desc
        filtered_items.sort(key=lambda x: x[1], reverse=True)
        
        print("\n--- Filtered Group Mentions (Count >= 2) ---")
        print(f"{'YPAA Group / Conference':<40} | {'Mentions'}")
        print("-" * 60)
        filtered_count_sum = 0
        for group, count in filtered_items:
            print(f"{group:<40} | {count}")
            filtered_count_sum += count
            
        print("\n--- Summary ---")
        print(f"Total Rows Processed: {len(rows)}")
        print(f"Total Mentions Identified: {total_mentions}")
        print(f"Mentions Grouped by a YPAA/Conference (Count >= {threshold}): {filtered_count_sum}")
        print(f"Mentions indicating a 'Yes' but no specific YPAA/Committee: {yes_unspecified_sum}")
        print(f"Mentions indicating 'No' or blank (Not Specified): {no_specified_sum}")
        print(f"Mentions that were 'Very Dissimilar' (One-off entries): {dissimilar_sum}")

    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    main()