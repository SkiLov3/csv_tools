#!/usr/bin/env python3
"""
Normalizes and counts YPAA committee names from survey or registration data.
"""
import csv
import re
from collections import Counter
from utils import (
    select_file_interactive,
    select_column_interactive,
    read_csv_with_fallback_encoding,
    create_base_argparser
)


# Unified normalization map for YPAA names
# Maps variations/typos to canonical names
YPAA_NORMALIZATION = {
    # SALTYPAA/SLUTYPAA variants -> UCYPAA
    'SALTYPAA': 'UCYPAA',
    'SLUTYPAA': 'UCYPAA',
    'SLTYPAA': 'UCYPAA',
    # Common typos
    'UCPAA': 'UCYPAA',
    'BUTTEY': 'BUTTEYPAA',
    'WAC': 'WACYPAA',
    'WACY': 'WACYPAA',
    'SACY': 'SACYPAA',
    'RENVY': 'RENVYPAA',
    'RENYPAA': 'RENVYPAA',
    'SWAC': 'SWACYPAA',
    'SWACYPA': 'SWACYPAA',
    'BURQUYPAA': 'BURQYPAA',
    'BURQYPQAA': 'BURQYPAA',
    'NACYPA': 'NACYPAA',
    'CCPAA': 'CCYPAA',
    'BELLYPA': 'BELLYPAA',
    'BACY': 'BACYPAA',
    'TITY': 'TITYPAA',
}

# Standardized "No" responses
NO_RESPONSES = frozenset({
    '', 'nan', 'no', 'nope', 'not yet', 'not right now', 'maybe',
    'not currently', 'not at this time', 'hell no', 'naur', 'n',
    'not yet!', 'not this year', 'there isnt one near me :(',
    'negative/supporter/cheerleader'
})

# Responses that indicate "Yes" without specifying a group
YES_RESPONSES = frozenset({
    'yes', 'why yes i am', 'yes .', 'yea', 'yes!'
})


def normalize_ypaa_name(name):
    """
    Normalize a YPAA name using the normalization map.
    """
    upper_name = name.upper()
    return YPAA_NORMALIZATION.get(upper_name, upper_name)


def extract_groups(name):
    """
    Extracts a list of standardized committee/group names from a string.
    Handles multiple groups (separated by /, &, and, ,) and typos.
    
    Returns:
        List of unique group names found
    """
    if not name or not name.strip():
        return ['Not Specified / Not a YPAA']
        
    name_lower = name.strip().lower()

    if name_lower in NO_RESPONSES:
        return ['Not Specified / Not a YPAA']

    if name_lower in YES_RESPONSES:
        return ['Yes, Unspecified Group']

    # Split by common separators: /, &, comma, ' and '
    parts = re.split(r'[/,&]|\s+and\s+', name)
    
    found_groups = []
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        part_lower = part.lower()
        
        # Try regex for YPAA pattern first
        match = re.search(r'\b([a-zA-Z]*YPAA)\b', part, re.IGNORECASE)
        if match:
            found_name = normalize_ypaa_name(match.group(1))
            found_groups.append(found_name)
            continue
            
        # Check typos map if regex failed
        for typo, correction in YPAA_NORMALIZATION.items():
            if typo.lower() in part_lower:
                found_groups.append(correction)
                break
        else:
            # If no YPAA found, check for Host/Advisory role
            if 'host' in part_lower or 'advisory' in part_lower:
                found_groups.append('Host / Advisory (Unspecified YPAA)')
                
    if found_groups:
        # Return unique groups, preserving order
        return list(dict.fromkeys(found_groups))
        
    # Fallback: check if contains "yes"
    if 'yes' in name_lower:
        return ['Yes, Unspecified Group']
         
    return [name.strip().title()]


def main():
    parser = create_base_argparser(
        "Analyze YPAA committee mentions from registration data."
    )
    parser.add_argument(
        '-p', '--products-column',
        help='Name of the products/quantity column (auto-detected if not provided)'
    )
    parser.add_argument(
        '-t', '--threshold',
        type=int,
        default=2,
        help='Minimum mention count to display (default: 2)'
    )
    args = parser.parse_args()
    
    print("--- YPAA Committee Analyzer ---")
    
    # Get file
    file_path = args.file
    if not file_path:
        file_path = select_file_interactive()
        if not file_path:
            return

    print(f"\nLoading {file_path}...")
    
    try:
        headers, rows = read_csv_with_fallback_encoding(file_path, use_dictreader=False)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return
    except UnicodeDecodeError as e:
        print(f"Error: Could not decode file - {e}")
        return
    except csv.Error as e:
        print(f"Error: CSV parsing failed - {e}")
        return

    # Select committee column
    column_name = select_column_interactive(
        headers, 
        args.column, 
        default_index=4,
        prompt_suffix=" for committee data"
    )
    column_index = headers.index(column_name)
    print(f"Analyzing Committee Column: '{column_name}'")

    # Select products column
    print("\n--- Select Products/Quantity Column ---")
    products_col = args.products_column
    
    # Try auto-detection if not specified
    if not products_col:
        for idx, col in enumerate(headers):
            if "products" in col.lower():
                products_col = col
                break
    
    if not products_col:
        products_col = select_column_interactive(
            headers, 
            None,
            prompt_suffix=" for registration counts"
        )
    elif products_col not in headers:
        print(f"Warning: Column '{products_col}' not found, selecting interactively.")
        products_col = select_column_interactive(headers)
    
    products_index = headers.index(products_col)
    print(f"Using Products Column: '{products_col}'")

    # Regex for product parsing
    product_pattern = re.compile(
        r'(.*?)\s*\(Amount:.*?, Quantity:\s*(\d+)(?:, Registration Type:\s*(.*?))?.*?\)'
    )

    all_groups = []
    total_registrations_processed = 0

    for row in rows:
        # 1. Determine Registration Count for this row
        reg_count = 0
        if len(row) > products_index:
            prod_cell = row[products_index]
            if prod_cell:
                lines = prod_cell.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("Total:") or line.startswith("Transaction ID:"):
                        continue
                    
                    match = product_pattern.search(line)
                    if match:
                        p_name = match.group(1).strip()
                        p_qty = int(match.group(2))
                        
                        if "Registration" in p_name:
                            reg_count += p_qty
        
        # Skip rows with no registrations
        if reg_count == 0:
            continue

        total_registrations_processed += reg_count

        # 2. Extract Committees
        if len(row) > column_index:
            val = row[column_index]
            groups = extract_groups(val)
            
            # Add to master list reg_count times (weighted)
            for _ in range(reg_count):
                all_groups.extend(groups)
        else:
            # Row exists but no committee column data
            for _ in range(reg_count):
                all_groups.append('Not Specified / Not a YPAA')

    # Calculate counts
    group_counts = Counter(all_groups)
    threshold = args.threshold
    
    filtered_items = []
    dissimilar_sum = 0
    no_specified_sum = 0
    yes_unspecified_sum = 0
    total_mentions_weighted = 0
    
    for group, count in group_counts.items():
        total_mentions_weighted += count
        
        if group == 'Not Specified / Not a YPAA':
            no_specified_sum += count
        elif group == 'Yes, Unspecified Group':
            yes_unspecified_sum += count
        elif count == 1:
            dissimilar_sum += count
        elif count >= threshold:
            filtered_items.append((group, count))
            
    # Sort descending
    filtered_items.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n--- Filtered Group Mentions (Weighted by Registration Count >= {threshold}) ---")
    print(f"{'YPAA Group / Conference':<40} | {'Weighted Count'}")
    print("-" * 60)
    filtered_count_sum = 0
    for group, count in filtered_items:
        print(f"{group:<40} | {count}")
        filtered_count_sum += count
        
    print("\n--- Summary ---")
    print(f"Total Rows Processed: {len(rows)}")
    print(f"Total Registered Attendees Counted: {total_registrations_processed}")
    print(f"Weighted Mentions Grouped by a YPAA/Conference: {filtered_count_sum}")
    print(f"Weighted Mentions indicating a 'Yes' but no specific YPAA: {yes_unspecified_sum}")
    print(f"Weighted Mentions indicating 'No' or blank: {no_specified_sum}")
    print(f"Weighted Mentions that were 'Very Dissimilar' (One-off entries): {dissimilar_sum}")


if __name__ == "__main__":
    main()