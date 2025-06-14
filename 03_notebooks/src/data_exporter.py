"""
Data Exporter Module
This module provides utilities for exporting pandas DataFrames to various formats
with interactive file naming and format selection.

Usage:
    from data_exporter import export_data_interactive
    
    # Export with interactive prompts
    export_data_interactive(df, output_path, original_filename="data.csv")
"""

import os
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_suggested_filename(original_filename, export_format, suffix=""):
    """
    Generate a suggested filename based on the original file and export format.
    
    Args:
        original_filename (str): Original file name
        export_format (str): Target export format (csv, excel, pickle, json, etc.)
        suffix (str): Optional suffix to add (e.g., "_processed", "_scaled")
    
    Returns:
        str: Suggested filename
    """
    if not original_filename:
        base_name = "data"
    else:
        # Remove extension from original filename
        base_name = Path(original_filename).stem
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # Add suffix if provided
    if suffix:
        suggested_name = f"{base_name}{suffix}_{timestamp}"
    else:
        suggested_name = f"{base_name}_exported_{timestamp}"
    
    # Add appropriate extension
    format_extensions = {
        'csv': '.csv',
        'excel': '.xlsx',
        'pickle': '.pkl',
        'json': '.json',
        'parquet': '.parquet',
        'feather': '.feather'
    }
    
    extension = format_extensions.get(export_format.lower(), '.csv')
    return suggested_name + extension


def export_data_interactive(df, output_path, original_filename=None, show_preview=True):
    """
    Export pandas DataFrame with interactive format and filename selection.
    
    Args:
        df (pd.DataFrame): DataFrame to export
        output_path (Path or str): Directory where file will be saved
        original_filename (str): Original filename for suggestion generation
        show_preview (bool): Whether to show data preview before export
    
    Returns:
        str: Path to exported file
    """
    output_path = Path(output_path)
    
    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)
    
    print("\n" + "="*60)
    print("📤 INTERACTIVE DATA EXPORT")
    print("="*60)
    
    # Show data preview
    if show_preview:
        print(f"\n📊 Data Preview:")
        print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        print("\n   First 3 rows:")
        print(df.head(3))
        print("\n   Column types:")
        print(df.dtypes.value_counts())
    
    # FORMAT SELECTION
    print("\n" + "-"*40)
    print("📁 SELECT EXPORT FORMAT")
    print("-"*40)
    
    export_formats = {
        1: ('csv', 'CSV - Comma Separated Values (most compatible)'),
        2: ('excel', 'Excel - Microsoft Excel format (.xlsx)'),
        3: ('pickle', 'Pickle - Python binary format (preserves data types)'),
        4: ('json', 'JSON - JavaScript Object Notation'),
        5: ('parquet', 'Parquet - Columnar storage (efficient for large data)'),
        6: ('feather', 'Feather - Fast binary format')
    }
    
    print("\n📋 Available export formats:")
    for key, (format_code, description) in export_formats.items():
        print(f"   {key}: {description}")
    
    # Get format choice
    print(f"\n💡 Recommended: CSV (1) for general use, Pickle (3) to preserve data types")
    while True:
        try:
            format_choice = input(f"\n>>> Choose export format (1-{len(export_formats)}) [Enter for CSV]: ").strip()
            if not format_choice:
                format_choice = 1
            else:
                format_choice = int(format_choice)
            
            if format_choice in export_formats:
                selected_format, format_description = export_formats[format_choice]
                break
            print(f"❌ Please enter a number between 1 and {len(export_formats)}")
        except ValueError:
            print("❌ Please enter a valid number or press Enter for CSV")
    
    print(f"\n✅ Selected format: {format_description}")
    
    # FILENAME SELECTION
    print("\n" + "-"*40)
    print("📝 SELECT FILENAME")
    print("-"*40)
    
    # Generate suggested filenames
    suggestions = []
    suffixes = ["", "_processed", "_cleaned", "_scaled", "_final"]
    
    for suffix in suffixes:
        suggested = get_suggested_filename(original_filename, selected_format, suffix)
        suggestions.append(suggested)
    
    print("\n💡 Suggested filenames:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}: {suggestion}")
    
    print(f"   {len(suggestions) + 1}: Enter custom filename")
    
    # Get filename choice
    while True:
        try:
            filename_choice = input(f"\n>>> Choose filename option (1-{len(suggestions) + 1}) [Enter for 1]: ").strip()
            if not filename_choice:
                filename_choice = 1
            else:
                filename_choice = int(filename_choice)
            
            if 1 <= filename_choice <= len(suggestions):
                final_filename = suggestions[filename_choice - 1]
                break
            elif filename_choice == len(suggestions) + 1:
                # Custom filename
                custom_name = input("\n>>> Enter custom filename (without extension): ").strip()
                if custom_name:
                    # Add appropriate extension
                    format_extensions = {
                        'csv': '.csv',
                        'excel': '.xlsx', 
                        'pickle': '.pkl',
                        'json': '.json',
                        'parquet': '.parquet',
                        'feather': '.feather'
                    }
                    extension = format_extensions.get(selected_format, '.csv')
                    final_filename = custom_name + extension
                    break
                else:
                    print("❌ Filename cannot be empty")
            else:
                print(f"❌ Please enter a number between 1 and {len(suggestions) + 1}")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Final file path
    final_path = output_path / final_filename
    
    # Check if file exists
    if final_path.exists():
        overwrite = input(f"\n⚠️  File '{final_filename}' already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite not in ['y', 'yes']:
            # Add timestamp to make unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = final_path.stem
            suffix = final_path.suffix
            final_filename = f"{stem}_{timestamp}{suffix}"
            final_path = output_path / final_filename
            print(f"✅ Using modified filename: {final_filename}")
    
    print(f"\n📤 Exporting to: {final_path}")
    
    # EXPORT DATA
    try:
        if selected_format == 'csv':
            export_csv(df, final_path)
        elif selected_format == 'excel':
            export_excel(df, final_path)
        elif selected_format == 'pickle':
            export_pickle(df, final_path)
        elif selected_format == 'json':
            export_json(df, final_path)
        elif selected_format == 'parquet':
            export_parquet(df, final_path)
        elif selected_format == 'feather':
            export_feather(df, final_path)
        
        # Verify export
        file_size = final_path.stat().st_size / 1024**2  # Size in MB
        
        print("\n" + "="*60)
        print("✅ EXPORT SUCCESSFUL!")
        print("="*60)
        print(f"   📁 File: {final_filename}")
        print(f"   📍 Location: {output_path}")
        print(f"   📊 Size: {file_size:.2f} MB")
        print(f"   📅 Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        return str(final_path)
        
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        logger.error(f"Export failed: {e}")
        raise


def export_csv(df, file_path):
    """Export DataFrame to CSV with encoding options."""
    print("🔄 Exporting to CSV...")
    
    # Ask about encoding
    encoding_options = {
        1: ('utf-8', 'UTF-8 (recommended, universal)'),
        2: ('utf-8-sig', 'UTF-8 with BOM (Excel compatible)'),
        3: ('latin-1', 'Latin-1 (Western European)')
    }
    
    print("\n📝 Select CSV encoding:")
    for key, (encoding, description) in encoding_options.items():
        print(f"   {key}: {description}")
    
    while True:
        try:
            encoding_choice = input("\n>>> Choose encoding (1-3) [Enter for UTF-8]: ").strip()
            if not encoding_choice:
                selected_encoding = 'utf-8'
                break
            else:
                encoding_choice = int(encoding_choice)
                if encoding_choice in encoding_options:
                    selected_encoding = encoding_options[encoding_choice][0]
                    break
            print("❌ Please enter 1, 2, 3, or press Enter for UTF-8")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Export with selected encoding
    df.to_csv(file_path, index=False, encoding=selected_encoding)
    print(f"✅ CSV exported with {selected_encoding} encoding")


def export_excel(df, file_path):
    """Export DataFrame to Excel with sheet options."""
    print("🔄 Exporting to Excel...")
    
    # Ask for sheet name
    sheet_name = input("\n>>> Enter sheet name [Enter for 'Data']: ").strip()
    if not sheet_name:
        sheet_name = 'Data'
    
    # Export to Excel
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"✅ Excel exported with sheet name '{sheet_name}'")


def export_pickle(df, file_path):
    """Export DataFrame to Pickle format."""
    print("🔄 Exporting to Pickle...")
    df.to_pickle(file_path)
    print("✅ Pickle exported (preserves all data types)")


def export_json(df, file_path):
    """Export DataFrame to JSON with orientation options."""
    print("🔄 Exporting to JSON...")
    
    # Ask about JSON orientation
    orient_options = {
        1: ('records', 'Array of objects (most readable)'),
        2: ('index', 'Object with index as keys'),
        3: ('values', 'Array of arrays (compact)'),
        4: ('table', 'Table schema format')
    }
    
    print("\n📝 Select JSON format:")
    for key, (orient, description) in orient_options.items():
        print(f"   {key}: {description}")
    
    while True:
        try:
            orient_choice = input("\n>>> Choose format (1-4) [Enter for records]: ").strip()
            if not orient_choice:
                selected_orient = 'records'
                break
            else:
                orient_choice = int(orient_choice)
                if orient_choice in orient_options:
                    selected_orient = orient_options[orient_choice][0]
                    break
            print("❌ Please enter 1, 2, 3, 4, or press Enter for records")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Export to JSON
    df.to_json(file_path, orient=selected_orient, indent=2)
    print(f"✅ JSON exported with '{selected_orient}' orientation")


def export_parquet(df, file_path):
    """Export DataFrame to Parquet format."""
    print("🔄 Exporting to Parquet...")
    try:
        df.to_parquet(file_path, index=False)
        print("✅ Parquet exported (efficient columnar format)")
    except ImportError:
        print("❌ Parquet export requires pyarrow or fastparquet")
        print("   Install with: pip install pyarrow")
        raise


def export_feather(df, file_path):
    """Export DataFrame to Feather format."""
    print("🔄 Exporting to Feather...")
    try:
        df.to_feather(file_path)
        print("✅ Feather exported (fast binary format)")
    except ImportError:
        print("❌ Feather export requires pyarrow")
        print("   Install with: pip install pyarrow")
        raise


# Convenience function for quick exports
def quick_export(df, output_path, filename, format_type='csv'):
    """
    Quick export without interactive prompts.
    
    Args:
        df (pd.DataFrame): DataFrame to export
        output_path (Path or str): Output directory
        filename (str): Filename (with or without extension)
        format_type (str): Export format ('csv', 'excel', 'pickle', 'json')
    
    Returns:
        str: Path to exported file
    """
    output_path = Path(output_path)
    
    # Ensure proper extension
    format_extensions = {
        'csv': '.csv',
        'excel': '.xlsx',
        'pickle': '.pkl', 
        'json': '.json',
        'parquet': '.parquet',
        'feather': '.feather'
    }
    
    if not any(filename.endswith(ext) for ext in format_extensions.values()):
        filename += format_extensions.get(format_type, '.csv')
    
    file_path = output_path / filename
    
    # Create directory if needed
    os.makedirs(output_path, exist_ok=True)
    
    # Export based on format
    if format_type == 'csv':
        df.to_csv(file_path, index=False)
    elif format_type == 'excel':
        df.to_excel(file_path, index=False, sheet_name='Data')
    elif format_type == 'pickle':
        df.to_pickle(file_path)
    elif format_type == 'json':
        df.to_json(file_path, orient='records', indent=2)
    elif format_type == 'parquet':
        df.to_parquet(file_path, index=False)
    elif format_type == 'feather':
        df.to_feather(file_path)
    
    print(f"✅ Quick export completed: {file_path}")
    return str(file_path)