import os
import shutil
import zipfile
import re

def flatten_directory(year_path):
    print(f"  Flattening directory: {year_path}")
    # Iterate through subdirectories inside the year folder
    # List contents again because unzipping might have added new folders
    for sub_item in os.listdir(year_path):
        sub_item_path = os.path.join(year_path, sub_item)
        
        # We only want to flatten directories, not files
        if os.path.isdir(sub_item_path):
            # Skip if it is a hidden directory or something we shouldn't touch?
            # For now assume all subdirs are targets like SG05...
            
            print(f"    Processing subdirectory: {sub_item}")
            # Move all files from subdirectory to year directory
            for root, dirs, files in os.walk(sub_item_path):
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(year_path, file)
                    
                    if src_file == dst_file:
                        continue

                    # Handle collisions
                    if os.path.exists(dst_file):
                        # print(f"      WARNING: File {file} already exists. Renaming...")
                        base, ext = os.path.splitext(file)
                        dst_file = os.path.join(year_path, f"{base}_dup{ext}")
                    
                    try:
                        shutil.move(src_file, dst_file)
                    except Exception as e:
                        print(f"      Error moving {file}: {e}")
            
            # Remove the empty subdirectory
            try:
                shutil.rmtree(sub_item_path)
                print(f"    Removed directory: {sub_item}")
            except Exception as e:
                print(f"    Error removing directory {sub_item}: {e}")

def process_zips_and_flatten(base_path):
    # Regex to match 4-digit year directories
    year_pattern = re.compile(r'^\d{4}$')

    years = []
    for item in os.listdir(base_path):
        if year_pattern.match(item):
            years.append(item)
    
    years.sort()

    for year in years:
        if int(year) < 2019:
            continue
            
        year_path = os.path.join(base_path, year)
        if not os.path.isdir(year_path):
            continue

        print(f"Processing Year: {year}")
        
        # 1. Unzip all .zip files
        zip_files = [f for f in os.listdir(year_path) if f.lower().endswith('.zip')]
        if zip_files:
            print(f"  Found {len(zip_files)} zip files.")
            for zip_file in zip_files:
                zip_path = os.path.join(year_path, zip_file)
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(year_path)
                        # print(f"    Unzipped: {zip_file}")
                    
                    # Remove zip file after successful extraction
                    os.remove(zip_path)
                except zipfile.BadZipFile:
                    print(f"    Error: Bad zip file {zip_file}")
                except Exception as e:
                    print(f"    Error unzipping {zip_file}: {e}")
        else:
            print("  No zip files found.")

        # 2. Flatten the directory (handle any folders created by unzipping)
        flatten_directory(year_path)

if __name__ == "__main__":
    base_dir = "/Users/eoseungyun/Desktop/project/DB_IFC/Data/Land_Cover_Info"
    process_zips_and_flatten(base_dir)
