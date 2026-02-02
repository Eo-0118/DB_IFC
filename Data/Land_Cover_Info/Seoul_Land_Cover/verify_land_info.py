import pandas as pd
import numpy as np

def verify_data():
    file_path = '/Users/eoseungyun/Desktop/project/DB_IFC/Data/Land_Cover_Info/Seoul_Land_Cover/Seoul_Land_info.csv'
    df = pd.read_csv(file_path)

    # 토지피복 관련 컬럼들 (주거~수역)
    land_cols = ['주거지역', '공업지역', '상업지역', '문화체육휴양지역', '교통지역', '공공시설지역', 
                 '농업지역', '산림지역', '초지', '습지', '나지', '수역']

    # 존재하는 컬럼만 선택
    cols_to_sum = [c for c in land_cols if c in df.columns]

    # 합계 계산
    df['CALC_SUM'] = df[cols_to_sum].sum(axis=1)

    # 차이 계산 (소수점 고려하여 절대값 차이)
    df['DIFF'] = (df['CALC_SUM'] - df['TOTAL_AREA_M2']).abs()

    # 오차 허용 범위 (부동소수점 오차 고려 0.01로 설정)
    tolerance = 0.01 

    mismatch = df[df['DIFF'] > tolerance]

    print("-" * 50)
    if mismatch.empty:
        print('✅ Verification SUCCESS: All rows match within tolerance.')
        print(f"Max Difference found: {df['DIFF'].max()}")
    else:
        print('❌ Verification FAILED: Some rows do not match.')
        print(f'Number of mismatches: {len(mismatch)}')
        print("\nTop 5 Mismatches:")
        print(mismatch[['YEAR', 'SIGUNGU_NM', 'CALC_SUM', 'TOTAL_AREA_M2', 'DIFF']].head())
    print("-" * 50)

if __name__ == "__main__":
    verify_data()
