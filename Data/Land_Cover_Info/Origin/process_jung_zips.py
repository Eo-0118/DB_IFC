import os
import shutil
import zipfile
import unicodedata

def normalize_string(s):
    # Normalize unicode characters to NFC to handle Hangul properly
    return unicodedata.normalize('NFC', s)

def flatten_directory(year_path):
    print(f"  Flattening directory: {year_path}")
    # Iterate through subdirectories inside the year folder
    
    for sub_item in os.listdir(year_path):
        sub_item_path = os.path.join(year_path, sub_item)
        
        # We only want to flatten directories, not files
        if os.path.isdir(sub_item_path):
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

def process_jung_zips_and_flatten(base_path):
    for item in os.listdir(base_path):
        # Normalize the item name to check for '중'
        normalized_item = normalize_string(item)
        
        # Check if directory ends with '중'
        if normalized_item.endswith('중'):
            year_path = os.path.join(base_path, item)
            
            if not os.path.isdir(year_path):
                continue
                
            print(f"Processing Directory: {item}")
            
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

            # 2. Flatten the directory
            flatten_directory(year_path)

if __name__ == "__main__":
    base_dir = "/Users/eoseungyun/Desktop/project/DB_IFC/Data/Land_Cover_Info"
    process_jung_zips_and_flatten(base_dir)
