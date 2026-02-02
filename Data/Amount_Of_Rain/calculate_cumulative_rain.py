
import csv
from datetime import datetime, timedelta

INPUT_FILE = 'rain_data.csv'
OUTPUT_FILE = 'cumulative_rain_data.csv'

def process_rainfall_period(period):
    """Processes a list of rows representing a consecutive rainfall period."""
    if not period:
        return None

    station = period[0]['지점']
    region_name = period[0]['지역명']
    start_date = period[0]['일시']
    end_date = period[-1]['일시']
    duration = len(period)
    cumulative_rain = sum(float(row['일강수량(mm)']) for row in period)

    return [station, region_name, start_date, end_date, duration, cumulative_rain]

def main():
    try:
        with open(INPUT_FILE, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            data = sorted(reader, key=lambda row: (row['지점'], row['일시']))

        results = []
        current_period = []
        current_station = None

        for row in data:
            station = row['지점']
            
            # Handle station change
            if station != current_station:
                if current_period:
                    processed_row = process_rainfall_period(current_period)
                    if processed_row:
                        results.append(processed_row)
                current_period = []
                current_station = station

            # Handle rainfall data
            try:
                rainfall = float(row['일강수량(mm)']) if row['일강수량(mm)'] else 0.0
            except (ValueError, TypeError):
                rainfall = 0.0 # Treat non-numeric or empty as no rain

            if rainfall > 0:
                current_period.append(row)
            else: # rainfall is 0 or less
                if current_period:
                    processed_row = process_rainfall_period(current_period)
                    if processed_row:
                        results.append(processed_row)
                    current_period = []

        # Process the last period at the end of the file
        if current_period:
            processed_row = process_rainfall_period(current_period)
            if processed_row:
                results.append(processed_row)

        # Write results to the output file
        header = ["지점", "지역명", "강수 시작일", "강수 종료일", "강수 기간", "기간 누적 강수량"]
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header)
            writer.writerows(results)

        print(f"Successfully created {OUTPUT_FILE}")

    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
