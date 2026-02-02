
import csv
import os
import re

REGION_MAP = {
    '400': '강남', '401': '서초', '402': '강동', '403': '송파', '404': '강서',
    '405': '양천', '406': '도봉', '407': '노원', '408': '동대문', '409': '중랑',
    '410': '기상청', '411': '마포', '412': '서대문', '413': '광진', '414': '성북',
    '415': '용산', '416': '은평', '417': '금천', '418': '한강', '419': '중구',
    '420': '북한산', '421': '성동', '422': '북악산', '423': '구로', '424': '강북',
    '425': '남현', '509': '관악', '510': '영등포', '889': '현충원'
}

INPUT_DIR = 'converted_data'
OUTPUT_FILE = 'combined_data.csv'

# Get file list and header from the first file
file_list = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')])
if not file_list:
    print("No CSV files found in the input directory.")
    exit()

with open(os.path.join(INPUT_DIR, file_list[0]), 'r', encoding='utf-8') as f:
    header = f.readline().strip().split(',')

# Prepare new header
new_header = [header[0]] + ['지역명'] + header[1:]

with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(new_header)

    # Process each file
    for filename in file_list:
        match = re.search(r'SURFACE_AWS_(\d+)_DAY', filename)
        if not match:
            continue
        
        region_code = match.group(1)
        region_name = REGION_MAP.get(region_code, '알 수 없음') # Default value if code not in map

        filepath = os.path.join(INPUT_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            next(reader) # Skip header
            for row in reader:
                # Insert region name into the row
                row.insert(1, region_name)
                writer.writerow(row)

print(f"All files have been combined into {OUTPUT_FILE}")
