#!/usr/bin/env python3
"""
Merge script for database and contents files.
Merges daily data files into main database and contents files.
"""

import argparse
import csv
import json
import os
import sys
from typing import List, Dict, Set


def load_csv_data(file_path: str) -> List[Dict[str, str]]:
    """Load CSV data and return as list of dictionaries."""
    data = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
    return data


def save_csv_data(file_path: str, data: List[Dict[str, str]]) -> None:
    """Save data to CSV file."""
    if not data:
        return
    
    fieldnames = data[0].keys()
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def load_json_data(file_path: str) -> List[Dict]:
    """Load JSON data and return as list of dictionaries."""
    data = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
    return data


def save_json_data(file_path: str, data: List[Dict]) -> None:
    """Save data to JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def merge_database(input_file: str, output_file: str) -> int:
    """
    Merge database files by adding new entries that don't exist in output.
    Returns the number of new entries added.
    """
    print(f"Merging database: {input_file} -> {output_file}")
    
    # Load existing data
    existing_data = load_csv_data(output_file)
    new_data = load_csv_data(input_file)
    
    if not new_data:
        print(f"No data found in {input_file}")
        return 0
    
    # Create set of existing URLs for fast lookup
    existing_urls: Set[str] = {row.get('URL', '') for row in existing_data}
    
    # Find new entries
    new_entries = []
    for row in new_data:
        url = row.get('URL', '')
        if url and url not in existing_urls:
            new_entries.append(row)
            existing_urls.add(url)  # Avoid duplicates within new data
    
    if not new_entries:
        print("No new entries to add to database")
        return 0
    
    # Merge data
    merged_data = existing_data + new_entries
    
    # Save merged data
    save_csv_data(output_file, merged_data)
    
    print(f"Added {len(new_entries)} new entries to {output_file}")
    return len(new_entries)


def merge_contents(input_file: str, output_file: str) -> int:
    """
    Merge contents files by adding new entries that don't exist in output.
    Returns the number of new entries added.
    """
    print(f"Merging contents: {input_file} -> {output_file}")
    
    # Load existing data
    existing_data = load_json_data(output_file)
    new_data = load_json_data(input_file)
    
    if not new_data:
        print(f"No data found in {input_file}")
        return 0
    
    # Create set of existing URLs for fast lookup
    existing_urls: Set[str] = {item.get('URL', '') for item in existing_data}
    
    # Find new entries
    new_entries = []
    for item in new_data:
        url = item.get('URL', '')
        if url and url not in existing_urls:
            new_entries.append(item)
            existing_urls.add(url)  # Avoid duplicates within new data
    
    if not new_entries:
        print("No new entries to add to contents")
        return 0
    
    # Merge data
    merged_data = existing_data + new_entries
    
    # Save merged data
    save_json_data(output_file, merged_data)
    
    print(f"Added {len(new_entries)} new entries to {output_file}")
    return len(new_entries)


def main():
    """Main function to handle command line arguments and execute merge operations."""
    parser = argparse.ArgumentParser(
        description="Merge daily database and contents files into main files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python merge.py
  python merge.py --database-in today-data.csv --database-out main-data.csv
  python merge.py --contents-in today-content.json --contents-out main-content.json
        """
    )
    
    parser.add_argument(
        '--database-in',
        default='database-today.csv',
        help='Input database CSV file (default: database-today.csv)'
    )
    
    parser.add_argument(
        '--database-out',
        default='database.csv',
        help='Output database CSV file (default: database.csv)'
    )
    
    parser.add_argument(
        '--contents-in',
        default='contents-today.json',
        help='Input contents JSON file (default: contents-today.json)'
    )
    
    parser.add_argument(
        '--contents-out',
        default='contents.json',
        help='Output contents JSON file (default: contents.json)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be merged without actually writing files'
    )
    
    args = parser.parse_args()
    
    print("=== Database and Contents Merge Tool ===")
    print(f"Database: {args.database_in} -> {args.database_out}")
    print(f"Contents: {args.contents_in} -> {args.contents_out}")
    print()
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")
        print()
    
    total_added = 0
    
    try:
        # Merge database
        if args.dry_run:
            # For dry run, just check what would be added
            existing_db = load_csv_data(args.database_out)
            new_db = load_csv_data(args.database_in)
            existing_urls = {row.get('URL', '') for row in existing_db}
            new_entries = [row for row in new_db if row.get('URL', '') and row.get('URL', '') not in existing_urls]
            print(f"Would add {len(new_entries)} new database entries")
        else:
            db_added = merge_database(args.database_in, args.database_out)
            total_added += db_added
        
        # Merge contents
        if args.dry_run:
            # For dry run, just check what would be added
            existing_content = load_json_data(args.contents_out)
            new_content = load_json_data(args.contents_in)
            existing_urls = {item.get('URL', '') for item in existing_content}
            new_entries = [item for item in new_content if item.get('URL', '') and item.get('URL', '') not in existing_urls]
            print(f"Would add {len(new_entries)} new content entries")
        else:
            content_added = merge_contents(args.contents_in, args.contents_out)
            total_added += content_added
        
        print()
        if args.dry_run:
            print("Dry run completed - no files were modified")
        else:
            print(f"Merge completed successfully! Total new entries: {total_added}")
        
    except Exception as e:
        print(f"Error during merge: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
