import pandas as pd
import os

# Define file paths
COMBINED_DATA_FILE = 'combined_data.csv'
OBS_AWS_FILE = 'obs_aws_utf8.csv'
RAIN_DATA_FILE = 'rain_data.csv'

def create_rain_data_from_combined():
    """
    Reads the combined_data.csv file and extracts relevant columns to create 
    the initial rain_data.csv file.
    """
    if not os.path.exists(COMBINED_DATA_FILE):
        print(f"Error: {COMBINED_DATA_FILE} not found.")
        return

    df = pd.read_csv(COMBINED_DATA_FILE, encoding='utf-8')
    rain_df = df[['지점', '지역명', '일시', '일강수량(mm)']]
    rain_df.to_csv(RAIN_DATA_FILE, index=False, encoding='utf-8')
    print(f"Successfully created {RAIN_DATA_FILE} from {COMBINED_DATA_FILE}")

def append_obs_aws_data():
    """
    Reads the obs_aws_utf8.csv file, processes it to calculate daily rainfall,
    and appends the result to the rain_data.csv file.
    """
    if not os.path.exists(OBS_AWS_FILE):
        print(f"Warning: {OBS_AWS_FILE} not found. Skipping append step.")
        return

    # Read the data, handling potential parsing errors
    try:
        df = pd.read_csv(OBS_AWS_FILE, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        print(f"Error reading {OBS_AWS_FILE}: {e}")
        return

    # Rename columns for consistency
    df = df.rename(columns={'강수량(mm)': '일강수량(mm)'})

    # Convert '일시' to datetime objects
    df['일시'] = pd.to_datetime(df['일시'], errors='coerce')
    df = df.dropna(subset=['일시'])  # Remove rows where date conversion failed

    # Group by day and aggregate
    daily_rain = df.groupby(df['일시'].dt.date).agg({
        '지점': 'first',
        '지점명': 'first',
        '일강수량(mm)': 'sum'
    }).reset_index()

    # Rename '일시' back to the original name for consistency
    daily_rain = daily_rain.rename(columns={'일시': '일시_date'})
    daily_rain['일시'] = daily_rain['일시_date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    # Reorder and select columns to match rain_data.csv
    daily_rain_final = daily_rain[['지점', '지점명', '일시', '일강수량(mm)']]
    daily_rain_final = daily_rain_final.rename(columns={'지점명': '지역명'})


    # Append to rain_data.csv
    daily_rain_final.to_csv(RAIN_DATA_FILE, mode='a', header=False, index=False, encoding='utf-8')
    print(f"Successfully appended data from {OBS_AWS_FILE} to {RAIN_DATA_FILE}")


def main():
    """
    Main function to coordinate the creation and updating of the rain_data.csv file.
    """
    create_rain_data_from_combined()
    append_obs_aws_data()

if __name__ == '__main__':
    main()