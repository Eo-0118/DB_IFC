
import pandas as pd

RAIN_DATA_FILE = 'rain_data.csv'

# Load the data
df = pd.read_csv(RAIN_DATA_FILE, encoding='utf-8')

# Filter for daily rainfall of 100mm or more
heavy_rainfall_df = df[df['일강수량(mm)'] >= 100]

# Group by region and collect the dates
heavy_rainfall_by_region = heavy_rainfall_df.groupby('지역명')['일시'].apply(list)

# Print the results
for region, dates in heavy_rainfall_by_region.items():
    print(f"지역: {region}")
    for date in dates:
        print(f"  - {date}")
    print("-" * 30)
