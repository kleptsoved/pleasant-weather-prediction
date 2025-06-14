"""
CSV File Handler Module - Enhanced for Multiple Datasets
This module provides utilities for setting up project paths and loading multiple CSV files
with automatic encoding and delimiter detection.

Expected project structure:
    Your Project/
    ├── 01_project_management/
    ├── 02_data/
    ├── 03_notebooks/         ← Run notebooks from here
    │   └── src/             ← This module lives here
    ├── 04_analyses/
    └── 05_results/
"""

import os
import sys
import chardet
import openpyxl
import pandas as pd
from pathlib import Path
import logging
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_subfolders(parent_path):
    """
    Get list of subfolders, with better error handling and debugging.
    """
    subfolders = []
    try:
        # List all items in the directory
        all_items = list(parent_path.iterdir())
        
        # Filter for directories only
        for item in all_items:
            try:
                if item.is_dir() and not item.name.startswith('.'):
                    subfolders.append(item)
            except (PermissionError, OSError) as e:
                print(f"⚠️  Skipping '{item.name}': {e}")
                continue
        
        # Sort the valid subfolders
        subfolders.sort(key=lambda x: x.name)
        
    except Exception as e:
        print(f"⚠️  Error listing directory contents: {e}")
    
    return subfolders


def setup_paths():
    """
    Set up project paths and folders interactively.
    Assumes notebooks are run from 03_notebooks/ directory.
    
    Returns:
        tuple: (project_root, input_path, output_path)
    """
    # Get current working directory (should be in 03_notebooks)
    current_dir = Path.cwd()
    
    # Navigate to project root (parent of 03_notebooks)
    if current_dir.name == '03_notebooks':
        project_root = current_dir.parent
    elif current_dir.parent.name == '03_notebooks':
        # If running from a subdirectory within 03_notebooks
        project_root = current_dir.parent.parent
    else:
        # Fallback: assume we're one level deep in project
        project_root = current_dir.parent
        print(f"⚠️  Warning: Expected to run from '03_notebooks' folder.")
    
    print(f"📍 Current directory: {current_dir}")
    print(f"📁 Project root: {project_root}")
    
    # List only directories (not files) in project root
    folders = get_subfolders(project_root)
    
    if not folders:
        print("❌ No folders found in project root directory.")
        sys.exit(1)
    
    # INPUT FOLDER SELECTION
    print("\n" + "="*60)
    print("📥 SELECT INPUT FOLDER")
    print("="*60)
    print("\n📋 Available folders in project:")
    for i, folder in enumerate(folders, start=1):
        print(f"   {i}: {folder.name}")
    
    while True:
        try:
            choice = int(input("\n>>> Choose input folder number (1-{}): ".format(len(folders))).strip()) - 1
            if 0 <= choice < len(folders):
                input_base = folders[choice]
                break
            print("❌ Please enter a number between 1 and {}".format(len(folders)))
        except ValueError:
            print("❌ Please enter a valid number.")
    
    print(f"\n✅ Selected: {input_base.name}")
    
    # Check for subfolders in input folder
    input_path = input_base
    subfolders = get_subfolders(input_base)
    
    # Always show subfolder status
    print("\n" + "-"*40)
    if subfolders:
        print(f"📂 Subfolders in '{input_base.name}':")
        print("   0: Use '{}' (parent folder)".format(input_base.name))
        for i, subfolder in enumerate(subfolders, start=1):
            print(f"   {i}: {subfolder.name}")
        
        while True:
            try:
                sub_choice = input("\n>>> Choose subfolder (0-{}) [Enter for 0]: ".format(len(subfolders))).strip()
                if not sub_choice:
                    sub_choice = 0
                else:
                    sub_choice = int(sub_choice)
                
                if sub_choice == 0:
                    input_path = input_base
                    break
                elif 1 <= sub_choice <= len(subfolders):
                    input_path = subfolders[sub_choice - 1]
                    break
                print("❌ Please enter a number between 0 and {}".format(len(subfolders)))
            except ValueError:
                print("❌ Please enter a valid number.")
    else:
        print(f"📂 No subfolders found in '{input_base.name}'")
        print("   Using parent folder directly")
        input_path = input_base
    
    # Check if input directory exists
    if not input_path.exists() or not input_path.is_dir():
        print(f"❌ Error: Input directory '{input_path}' does not exist or is not a directory.")
        sys.exit(1)
    
    print(f"\n✅ Input path set to: {input_path}")
    
    # OUTPUT FOLDER SELECTION
    print("\n\n" + "="*60)
    print("📤 SELECT OUTPUT FOLDER")
    print("="*60)
    print("\n📋 Available folders in project:")
    for i, folder in enumerate(folders, start=1):
        print(f"   {i}: {folder.name}")
    print(f"\n   💡 Press Enter to use input folder: {input_path.relative_to(project_root)}")
    
    while True:
        try:
            choice_str = input("\n>>> Choose output folder number (1-{}) [Enter for input folder]: ".format(len(folders))).strip()
            if not choice_str:
                output_base = input_base
                output_path = input_path
                break
            else:
                choice = int(choice_str) - 1
                if 0 <= choice < len(folders):
                    output_base = folders[choice]
                    output_path = output_base
                    break
                print("❌ Please enter a number between 1 and {}".format(len(folders)))
        except ValueError:
            print("❌ Please enter a valid number or press Enter.")
    
    # If different folder selected, check for subfolders
    if not choice_str:  # User pressed Enter to use input folder
        output_path = input_path
    else:  # User selected a folder (even if it's the same as input)
        print(f"\n✅ Selected: {output_base.name}")
        
        # Get subfolders using the helper function
        out_subfolders = get_subfolders(output_base)
        
        # Always show subfolder prompt
        print("\n" + "-"*40)
        if out_subfolders:
            print(f"📂 Subfolders in '{output_base.name}':")
            print("   0: Use '{}' (parent folder)".format(output_base.name))
            for i, subfolder in enumerate(out_subfolders, start=1):
                print(f"   {i}: {subfolder.name}")
            
            while True:
                try:
                    sub_choice = input("\n>>> Choose subfolder (0-{}) [Enter for 0]: ".format(len(out_subfolders))).strip()
                    if not sub_choice:
                        sub_choice = 0
                    else:
                        sub_choice = int(sub_choice)
                    
                    if sub_choice == 0:
                        output_path = output_base
                        break
                    elif 1 <= sub_choice <= len(out_subfolders):
                        output_path = out_subfolders[sub_choice - 1]
                        break
                    print("❌ Please enter a number between 0 and {}".format(len(out_subfolders)))
                except ValueError:
                    print("❌ Please enter a valid number.")
        else:
            print(f"📂 No subfolders found in '{output_base.name}'")
            print("   Using parent folder directly")
            output_path = output_base
    
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    print("\n\n" + "="*60)
    print("✅ PROJECT SETUP COMPLETE!")
    print("="*60)
    print(f"\n   📥 Input path:  {input_path}")
    print(f"   📤 Output path: {output_path}")
    print("\n" + "="*60)
    
    return project_root, input_path, output_path


def load_pickle_file(file_path):
    """Load a pickle file."""
    print(f"\n🥒 Loading pickle file: {file_path.name}")
    
    try:
        # Try loading with pandas first (for DataFrame pickles)
        df = pd.read_pickle(file_path)
        
        # Check if it's actually a DataFrame
        if isinstance(df, pd.DataFrame):
            return df
        else:
            print(f"⚠️  Warning: Pickle file contains {type(df).__name__}, not a DataFrame")
            # Try to convert to DataFrame if possible
            if hasattr(df, '__iter__') and not isinstance(df, str):
                return pd.DataFrame(df)
            else:
                raise ValueError(f"Cannot convert {type(df).__name__} to DataFrame")
                
    except Exception as e:
        print(f"❌ Error loading pickle file: {e}")
        # Try with regular pickle as fallback
        try:
            import pickle
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            if isinstance(data, pd.DataFrame):
                return data
            elif isinstance(data, dict):
                return pd.DataFrame(data)
            elif isinstance(data, list):
                return pd.DataFrame(data)
            else:
                raise ValueError(f"Unsupported pickle content type: {type(data).__name__}")
        except Exception as e2:
            print(f"❌ Failed to load pickle file: {e2}")
            raise


def load_multiple_datasets(input_path, required_columns=None):
    """
    Load multiple data files with automatic format detection.
    
    Args:
        input_path (Path or str): Directory containing data files
        required_columns (list): List of required column names (optional)
    
    Returns:
        dict: Dictionary with filenames as keys and dataframes as values
    """
    input_path = Path(input_path)
    
    # Define supported file extensions
    supported_extensions = {
        'csv': '*.csv',
        'excel': ['*.xlsx', '*.xls'],
        'pickle': ['*.pkl', '*.pickle']
    }
    
    # Find all supported files
    all_files = []
    file_types = {}
    
    # CSV files
    csv_files = list(input_path.glob(supported_extensions['csv']))
    for f in csv_files:
        all_files.append(f)
        file_types[f] = 'csv'
    
    # Excel files
    for pattern in supported_extensions['excel']:
        excel_files = list(input_path.glob(pattern))
        for f in excel_files:
            all_files.append(f)
            file_types[f] = 'excel'
    
    # Pickle files
    for pattern in supported_extensions['pickle']:
        pkl_files = list(input_path.glob(pattern))
        for f in pkl_files:
            all_files.append(f)
            file_types[f] = 'pickle'
    
    # Sort files by name
    all_files.sort(key=lambda x: x.name)
    
    if not all_files:
        print(f"❌ No supported data files found in: {input_path}")
        raise FileNotFoundError(f"No supported data files found in {input_path}")
    
    print("\n📋 Available data files:")
    for i, f in enumerate(all_files, start=1):
        file_type = file_types[f]
        type_emoji = {'csv': '📊', 'excel': '📗', 'pickle': '🥒'}[file_type]
        print(f"   {i}: {type_emoji} {f.name} ({file_type.upper()})")
    
    # Ask user how they want to select files
    print("\n🔍 How would you like to select files?")
    print("   1: Select specific files")
    print("   2: Load all files")
    print("   3: Load files by type (CSV, Excel, etc.)")
    print("   4: Load files matching a pattern")
    
    while True:
        try:
            mode = int(input("\n>>> Choose selection mode (1-4): ").strip())
            if 1 <= mode <= 4:
                break
            print("❌ Please enter a number between 1 and 4")
        except ValueError:
            print("❌ Please enter a valid number.")
    
    selected_files = []
    
    if mode == 1:  # Select specific files
        print("\n📌 Select files (separate numbers with commas, e.g., 1,3,5)")
        print("   Or use ranges (e.g., 1-3,5,7-9)")
        print("   Press Enter to select all files")
        
        selection = input("\n>>> Enter file numbers: ").strip()
        
        if not selection:  # Select all
            selected_files = all_files
        else:
            # Parse selection
            indices = parse_selection(selection, len(all_files))
            selected_files = [all_files[i] for i in indices]
    
    elif mode == 2:  # Load all files
        selected_files = all_files
        print(f"\n✅ Selected all {len(all_files)} files")
    
    elif mode == 3:  # Load by type
        print("\n📁 Select file type:")
        print("   1: CSV files only")
        print("   2: Excel files only")
        print("   3: Pickle files only")
        
        while True:
            try:
                type_choice = int(input("\n>>> Choose file type (1-3): ").strip())
                if 1 <= type_choice <= 3:
                    break
                print("❌ Please enter a number between 1 and 3")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        type_map = {1: 'csv', 2: 'excel', 3: 'pickle'}
        selected_type = type_map[type_choice]
        selected_files = [f for f in all_files if file_types[f] == selected_type]
        print(f"\n✅ Selected {len(selected_files)} {selected_type.upper()} files")
    
    elif mode == 4:  # Pattern matching
        pattern = input("\n>>> Enter filename pattern (e.g., *weather*, iris*): ").strip()
        selected_files = [f for f in all_files if pattern.replace('*', '') in f.name]
        print(f"\n✅ Found {len(selected_files)} files matching '{pattern}'")
    
    if not selected_files:
        print("❌ No files selected")
        return {}
    
    # Load selected files
    print(f"\n🔄 Loading {len(selected_files)} files...")
    loaded_data = {}
    errors = []
    
    for i, file_path in enumerate(selected_files, start=1):
        file_type = file_types[file_path]
        print(f"\n[{i}/{len(selected_files)}] Loading: {file_path.name}")
        
        try:
            if file_type == 'csv':
                df = load_csv_file_auto(file_path)
            elif file_type == 'excel':
                df = load_excel_file_auto(file_path)
            elif file_type == 'pickle':
                df = load_pickle_file(file_path)
            
            # Store with filename as key
            loaded_data[file_path.name] = df
            print(f"   ✅ Loaded: {df.shape[0]} rows × {df.shape[1]} columns")
            
            # Check required columns if specified
            if required_columns:
                missing_cols = set(required_columns) - set(df.columns)
                if missing_cols:
                    print(f"   ⚠️  Missing columns: {missing_cols}")
                    
        except Exception as e:
            errors.append((file_path.name, str(e)))
            print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 LOADING SUMMARY")
    print("="*60)
    print(f"✅ Successfully loaded: {len(loaded_data)} files")
    if errors:
        print(f"❌ Failed to load: {len(errors)} files")
        for fname, error in errors:
            print(f"   - {fname}: {error}")
    
    # Display loaded datasets info
    if loaded_data:
        print("\n📋 Loaded datasets:")
        for fname, df in loaded_data.items():
            print(f"   - {fname}: {df.shape[0]} rows × {df.shape[1]} columns")
    
    return loaded_data


def parse_selection(selection_str, max_num):
    """Parse comma-separated numbers and ranges into a list of indices."""
    indices = []
    parts = selection_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # Handle range
            start, end = part.split('-')
            start = int(start.strip()) - 1
            end = int(end.strip()) - 1
            indices.extend(range(start, end + 1))
        else:
            # Single number
            indices.append(int(part) - 1)
    
    # Filter valid indices
    valid_indices = [i for i in indices if 0 <= i < max_num]
    return sorted(set(valid_indices))


def load_csv_file_auto(file_path):
    """Load CSV file with automatic encoding and delimiter detection."""
    # Detect encoding
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
    encoding = result['encoding']
    
    # Try common delimiters
    delimiters = [',', ';', '\t', '|']
    
    for delim in delimiters:
        try:
            df = pd.read_csv(file_path, encoding=encoding, sep=delim)
            # Check if it looks reasonable (more than 1 column)
            if len(df.columns) > 1:
                return df
        except:
            continue
    
    # If all fail, default to comma
    return pd.read_csv(file_path, encoding=encoding)


def load_excel_file_auto(file_path):
    """Load Excel file, automatically selecting first sheet with data."""
    excel_file = pd.ExcelFile(file_path)
    
    # If only one sheet, use it
    if len(excel_file.sheet_names) == 1:
        return pd.read_excel(file_path, sheet_name=excel_file.sheet_names[0])
    
    # Otherwise, try to find the sheet with most data
    best_sheet = None
    max_rows = 0
    
    for sheet in excel_file.sheet_names:
        try:
            df = pd.read_excel(file_path, sheet_name=sheet)
            if len(df) > max_rows:
                max_rows = len(df)
                best_sheet = sheet
        except:
            continue
    
    if best_sheet:
        return pd.read_excel(file_path, sheet_name=best_sheet)
    else:
        # Fall back to first sheet
        return pd.read_excel(file_path, sheet_name=excel_file.sheet_names[0])


def batch_process_datasets(datasets_dict, process_func, *args, **kwargs):
    """
    Apply a processing function to multiple datasets.
    
    Args:
        datasets_dict: Dictionary of datasets from load_multiple_datasets
        process_func: Function to apply to each dataset
        *args, **kwargs: Arguments to pass to process_func
    
    Returns:
        dict: Dictionary with same keys and processed dataframes as values
    """
    processed = {}
    
    print(f"\n🔄 Processing {len(datasets_dict)} datasets...")
    
    for fname, df in datasets_dict.items():
        print(f"\n📊 Processing: {fname}")
        try:
            processed[fname] = process_func(df, *args, **kwargs)
            print(f"   ✅ Processed successfully")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            processed[fname] = df  # Keep original if processing fails
    
    return processed


def save_multiple_datasets(datasets_dict, output_path, format='csv', prefix='processed_'):
    """
    Save multiple datasets to files.
    
    Args:
        datasets_dict: Dictionary of datasets
        output_path: Path to save files
        format: Output format ('csv', 'excel', 'pickle')
        prefix: Prefix to add to filenames
    """
    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True)
    
    print(f"\n💾 Saving {len(datasets_dict)} datasets to {output_path}")
    
    for fname, df in datasets_dict.items():
        # Create new filename with prefix
        base_name = Path(fname).stem
        
        if format == 'csv':
            new_name = f"{prefix}{base_name}.csv"
            df.to_csv(output_path / new_name, index=False)
        elif format == 'excel':
            new_name = f"{prefix}{base_name}.xlsx"
            df.to_excel(output_path / new_name, index=False)
        elif format == 'pickle':
            new_name = f"{prefix}{base_name}.pkl"
            df.to_pickle(output_path / new_name)
        
        print(f"   ✅ Saved: {new_name}")
    
    print(f"\n✅ All files saved to: {output_path}")


# Original single-file loading functions (kept for compatibility)
def load_data_with_detection_enhanced(input_path, required_columns=None):
    """
    Load a data file with automatic format detection AND return the filename.
    
    Args:
        input_path (Path or str): Directory containing data files
        required_columns (list): List of required column names (optional)
    
    Returns:
        tuple: (pd.DataFrame, str) - Loaded dataframe and selected filename
    """
    input_path = Path(input_path)
    
    # Define supported file extensions
    supported_extensions = {
        'csv': '*.csv',
        'excel': ['*.xlsx', '*.xls'],
        'pickle': ['*.pkl', '*.pickle']
    }
    
    # Find all supported files
    all_files = []
    file_types = {}
    
    # CSV files
    csv_files = list(input_path.glob(supported_extensions['csv']))
    for f in csv_files:
        all_files.append(f)
        file_types[f] = 'csv'
    
    # Excel files
    for pattern in supported_extensions['excel']:
        excel_files = list(input_path.glob(pattern))
        for f in excel_files:
            all_files.append(f)
            file_types[f] = 'excel'
    
    # Pickle files
    for pattern in supported_extensions['pickle']:
        pkl_files = list(input_path.glob(pattern))
        for f in pkl_files:
            all_files.append(f)
            file_types[f] = 'pickle'
    
    # Sort files by name
    all_files.sort(key=lambda x: x.name)
    
    if not all_files:
        print(f"❌ No supported data files found in: {input_path}")
        raise FileNotFoundError(f"No supported data files found in {input_path}")
    
    print("\n📋 Available data files:")
    for i, f in enumerate(all_files, start=1):
        file_type = file_types[f]
        type_emoji = {'csv': '📊', 'excel': '📗', 'pickle': '🥒'}[file_type]
        print(f"   {i}: {type_emoji} {f.name} ({file_type.upper()})")
    
    # Prompt user to choose a file
    while True:
        try:
            choice = int(input("\n>>> Choose file number (1-{}): ".format(len(all_files))).strip()) - 1
            if 0 <= choice < len(all_files):
                break
            print("❌ Please enter a number between 1 and {}".format(len(all_files)))
        except ValueError:
            print("❌ Please enter a valid number.")
    
    file_path = all_files[choice]
    file_type = file_types[file_path]
    selected_filename = file_path.name  # Capture the filename
    
    print(f"\n✅ Selected file: {selected_filename} ({file_type.upper()})")
    
    # Load based on file type (existing code)
    if file_type == 'csv':
        df = load_csv_file(file_path)
    elif file_type == 'excel':
        df = load_excel_file(file_path)
    elif file_type == 'pickle':
        df = load_pickle_file(file_path)
    
    print(f"\n✅ Loaded data: {df.shape[0]} rows × {df.shape[1]} columns")
    
    return df, selected_filename  # Return both dataframe and filename


def load_csv_file(file_path):
    """Load a CSV file with encoding and delimiter detection."""
    print(f"\n🔍 Detecting encoding for {file_path.name}...")
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
    encoding = result['encoding']
    confidence = result['confidence']
    print(f"   Detected encoding: {encoding} (confidence: {confidence:.1%})")
    
    # Analyze delimiter options
    print("\n🔍 Analyzing potential delimiters:")
    delimiters = [',', ';', '\t', '|']
    delimiter_options = {}
    
    for i, delim in enumerate(delimiters, start=1):
        try:
            preview_df = pd.read_csv(file_path, engine='python', encoding=encoding, 
                                   sep=delim, nrows=3)
            col_count = len(preview_df.columns)
            delimiter_options[i] = (delim, col_count)
            delim_display = 'TAB' if delim == '\t' else f"'{delim}'"
            print(f"   {i}: Delimiter {delim_display} - Found {col_count} columns")
        except Exception as e:
            delim_display = 'TAB' if delim == '\t' else f"'{delim}'"
            print(f"   {i}: Error with delimiter {delim_display}")
    
    # Suggest the delimiter with the most columns
    if delimiter_options:
        suggested = max(delimiter_options, key=lambda k: delimiter_options[k][1])
        delim_display = 'TAB' if delimiter_options[suggested][0] == '\t' else f"'{delimiter_options[suggested][0]}'"
        print(f"\n💡 Suggested: Option {suggested} ({delim_display}) "
              f"with {delimiter_options[suggested][1]} columns")
    else:
        print("❌ Error: No valid delimiters found. Please check the file format.")
        raise ValueError("No valid delimiters found")
    
    # Prompt user to choose delimiter
    while True:
        try:
            delim_choice = input("\n>>> Choose delimiter option (1-{}) [Enter for suggested]: ".format(len(delimiter_options))).strip()
            if not delim_choice:
                delim_choice = suggested
            else:
                delim_choice = int(delim_choice)
            if delim_choice in delimiter_options:
                break
            print("❌ Please enter a number between 1 and {} or press Enter for default.".format(len(delimiter_options)))
        except ValueError:
            print("❌ Please enter a valid number or press Enter for default.")
    
    chosen_delim = delimiter_options[delim_choice][0]
    delim_display = 'TAB' if chosen_delim == '\t' else f"'{chosen_delim}'"
    print(f"\n✅ Using delimiter: {delim_display}")
    
    # Load the full CSV
    return pd.read_csv(file_path, encoding=encoding, sep=chosen_delim)


def load_excel_file(file_path):
    """Load an Excel file, handling multiple sheets if present."""
    print(f"\n📗 Loading Excel file: {file_path.name}")
    
    # First, get all sheet names
    try:
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        if len(sheet_names) == 1:
            # Only one sheet, load it directly
            print(f"   Loading single sheet: '{sheet_names[0]}'")
            return pd.read_excel(file_path, sheet_name=sheet_names[0])
        else:
            # Multiple sheets, let user choose
            print(f"\n📑 Found {len(sheet_names)} sheets:")
            for i, sheet in enumerate(sheet_names, start=1):
                # Try to get sheet info
                try:
                    preview_df = pd.read_excel(file_path, sheet_name=sheet, nrows=0)
                    col_count = len(preview_df.columns)
                    print(f"   {i}: '{sheet}' ({col_count} columns)")
                except:
                    print(f"   {i}: '{sheet}'")
            
            # Ask user to choose
            while True:
                try:
                    sheet_choice = input("\n>>> Choose sheet number (1-{}): ".format(len(sheet_names))).strip()
                    sheet_idx = int(sheet_choice) - 1
                    if 0 <= sheet_idx < len(sheet_names):
                        selected_sheet = sheet_names[sheet_idx]
                        break
                    print("❌ Please enter a number between 1 and {}".format(len(sheet_names)))
                except ValueError:
                    print("❌ Please enter a valid number.")
            
            print(f"\n✅ Loading sheet: '{selected_sheet}'")
            return pd.read_excel(file_path, sheet_name=selected_sheet)
            
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        raise


# Example usage in your main script:
if __name__ == "__main__":
    # Set up paths
    project_root, input_path, output_path = setup_paths()
    
    # Option 1: Load a single dataset (original functionality)
    # df, filename = load_data_with_detection_enhanced(input_path)
    
    # Option 2: Load multiple datasets (new functionality)
    datasets = load_multiple_datasets(input_path)
    
    # Example: Apply a simple processing function to all datasets
    def clean_data(df):
        # Remove rows with any missing values
        return df.dropna()
    
    # Process all datasets
    cleaned_datasets = batch_process_datasets(datasets, clean_data)
    
    # Save all processed datasets
    save_multiple_datasets(cleaned_datasets, output_path, format='csv', prefix='cleaned_')
    
    # Or work with individual datasets
    # for filename, df in datasets.items():
    #     print(f"\nAnalyzing {filename}:")
    #     print(df.describe())