import pandas as pd
import os
import glob
import numpy as np

def interpolate_impervious_data():
    folder_path = '/Users/eoseungyun/Desktop/project/DB_IFC/Data/Land_Cover_Info/ImperviousData'
    files = glob.glob(os.path.join(folder_path, '*_impervious_summary.csv'))
    
    if not files:
        print("No impervious summary files found.")
        return

    # 1. Load Data
    df_list = []
    for f in files:
        year = int(os.path.basename(f).split('_')[0])
        temp_df = pd.read_csv(f)
        temp_df['YEAR'] = year
        df_list.append(temp_df)
    
    full_df = pd.concat(df_list, ignore_index=True)
    
    # 2. Select Columns and Prepare for Interpolation
    # We mainly need Year, Sigungu, Impervious_Area, Total_Area
    # Pervious and Ratio can be recalculated later
    cols = ['YEAR', 'SIGUNGU_NM', 'IMPERVIOUS_AREA_M2', 'TOTAL_AREA_M2']
    data = full_df[cols].copy()
    
    # Get all unique Sigungus
    sigungus = data['SIGUNGU_NM'].unique()
    years = np.arange(2000, 2025) # 2000 to 2024
    
    # Create the complete index (Year x Sigungu)
    # Using MultiIndex to easily reindex
    idx = pd.MultiIndex.from_product([sigungus, years], names=['SIGUNGU_NM', 'YEAR'])
    
    # Reindex the data dataframe
    data = data.set_index(['SIGUNGU_NM', 'YEAR']).reindex(idx).reset_index()
    
    # 3. Perform Linear Interpolation Group-wise
    # Since we reindexed, missing years have NaN values now.
    # We group by Sigungu and interpolate within each group.
    
    # Sort to ensure time order before interpolation
    data = data.sort_values(by=['SIGUNGU_NM', 'YEAR'])
    
    # Helper function to apply to each group
    def interpolate_group(group):
        # Interpolate linear
        group['IMPERVIOUS_AREA_M2'] = group['IMPERVIOUS_AREA_M2'].interpolate(method='linear')
        group['TOTAL_AREA_M2'] = group['TOTAL_AREA_M2'].interpolate(method='linear')
        
        # Optional: Backfill/Forwardfill if limits are NaN (e.g. if 2000 was missing, but it is present)
        # But here 2000 is present. If 2025 is missing, extrapolation might be needed or just ffill.
        # Our data has 2025, so straightforward interpolation should work for 2000-2025.
        return group

    interpolated_df = data.groupby('SIGUNGU_NM').apply(interpolate_group).reset_index(drop=True)
    
    # 4. Recalculate Calculated Fields
    # PERVIOUS = TOTAL - IMPERVIOUS
    interpolated_df['PERVIOUS_AREA_M2'] = interpolated_df['TOTAL_AREA_M2'] - interpolated_df['IMPERVIOUS_AREA_M2']
    
    # RATIO = IMPERVIOUS / TOTAL * 100
    interpolated_df['IMPERVIOUS_RATIO'] = (interpolated_df['IMPERVIOUS_AREA_M2'] / interpolated_df['TOTAL_AREA_M2'] * 100)
    
    # Organize columns
    final_cols = ['YEAR', 'SIGUNGU_NM', 'PERVIOUS_AREA_M2', 'IMPERVIOUS_AREA_M2', 'TOTAL_AREA_M2', 'IMPERVIOUS_RATIO']
    final_df = interpolated_df[final_cols]
    
    # Round areas to 2 decimal places, Ratio to 4
    final_df = final_df.round({'PERVIOUS_AREA_M2': 2, 'IMPERVIOUS_AREA_M2': 2, 'TOTAL_AREA_M2': 2, 'IMPERVIOUS_RATIO': 4})
    
    # 5. Save Combined CSV
    output_path = os.path.join(folder_path, 'Seoul_ImperviousData_2000_2024.csv')
    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Saved complete interpolated data to {output_path}")
    print(final_df.head(10))

if __name__ == "__main__":
    interpolate_impervious_data()
