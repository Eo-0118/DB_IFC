import pandas as pd
import os
import glob
import numpy as np

def process_mixed_land_cover():
    base_folder = '.'
    
    # 1. 대상 파일 찾기
    all_files = glob.glob(os.path.join(base_folder, '**', '*_lv2_summary.csv'), recursive=True)
    print(f"Found {len(all_files)} LV2 summary files.")
    
    df_list = []
    processed_years = set()

    # 분류 맵핑 정의
    code_map = {
        '110': '주거지역',
        '120': '공업지역',
        '130': '상업지역',
        '140': '문화체육휴양지역',
        '150': '교통지역',
        '160': '공공시설지역'
    }
    # 200~700번대 대분류 맵핑
    major_map = {
        '2': '농업지역',
        '3': '산림지역',
        '4': '초지',
        '5': '습지',
        '6': '나지',
        '7': '수역'
    }

    for file_path in all_files:
        filename = os.path.basename(file_path)
        try:
            year_str = filename.split('_')[0]
            year = int(year_str)
        except:
            continue
            
        if year in processed_years: continue
        processed_years.add(year)
        
        print(f"Processing {filename} (Year: {year})...")
        df = pd.read_csv(file_path)
        
        # 컬럼 찾기
        code_col = None
        for col in ['L2_CODE', 'LV2_CODE', 'CODE', 'L3_CODE']:
            if col in df.columns:
                code_col = col
                break
        if not code_col: continue
            
        # 분류 로직 함수
        def categorize(code):
            code_str = str(code)
            # 숫자형 변환 시도 (float string 대응)
            try:
                code_str = str(int(float(code_str)))
            except:
                return 'Unknown'
            
            # 길이 보정 (2자리인 경우 등)
            if len(code_str) == 2:
                # 11 -> 110
                if code_str.startswith('1'):
                    code_str = code_str + '0'
                else:
                    pass # 21, 22 등... 
            
            first_digit = code_str[0]
            
            if first_digit == '1':
                # 시가화지역: 중분류 코드 그대로 사용
                if len(code_str) >= 2:
                    norm_code = code_str[:2] + '0'
                    if norm_code in code_map:
                        return code_map[norm_code]
                return '기타시가화'
                
            elif first_digit in major_map:
                # 2~7번대: 대분류로 통합
                return major_map[first_digit]
            else:
                return '기타'

        df['CATEGORY'] = df[code_col].apply(categorize)
        
        # 집계
        grouped = df.groupby(['SIGUNGU_NM', 'CATEGORY'])['AREA_M2'].sum().reset_index()
        grouped['YEAR'] = year
        df_list.append(grouped)

    # 통합
    if not df_list:
        print("No data found.")
        return

    full_df = pd.concat(df_list, ignore_index=True)
    
    # 피벗 (컬럼으로 변환)
    pivoted = full_df.pivot_table(index=['YEAR', 'SIGUNGU_NM'], columns='CATEGORY', values='AREA_M2', fill_value=0)
    pivoted = pivoted.reset_index()
    
    # 컬럼 순서 정렬 (보기 좋게)
    desired_order = ['YEAR', 'SIGUNGU_NM', 
                     '주거지역', '공업지역', '상업지역', '문화체육휴양지역', '교통지역', '공공시설지역',
                     '농업지역', '산림지역', '초지', '습지', '나지', '수역']
    
    # 실제 존재하는 컬럼만 선택
    existing_cols = [c for c in desired_order if c in pivoted.columns]
    # 혹시 기타 등이 있으면 추가
    remaining = [c for c in pivoted.columns if c not in existing_cols]
    final_cols = ['YEAR', 'SIGUNGU_NM'] + [c for c in existing_cols if c not in ['YEAR', 'SIGUNGU_NM']] + remaining
    
    pivoted = pivoted[final_cols]

    # 보간 (2000-2024)
    years_range = np.arange(2000, 2025)
    sigungus = pivoted['SIGUNGU_NM'].unique()
    idx = pd.MultiIndex.from_product([sigungus, years_range], names=['SIGUNGU_NM', 'YEAR'])
    
    pivoted = pivoted.set_index(['SIGUNGU_NM', 'YEAR']).reindex(idx).reset_index()
    pivoted = pivoted.sort_values(by=['SIGUNGU_NM', 'YEAR'])
    
    def interpolate_group(group):
        numeric_cols = group.select_dtypes(include=[np.number]).columns
        # YEAR 제외
        cols_to_interp = [c for c in numeric_cols if c != 'YEAR']
        group[cols_to_interp] = group[cols_to_interp].interpolate(method='linear')
        return group

    final_df = pivoted.groupby('SIGUNGU_NM').apply(interpolate_group).reset_index(drop=True)
    final_df = final_df.fillna(0)
    
    # 반올림 및 총면적 계산 (검증용)
    area_cols = [c for c in final_df.columns if c not in ['YEAR', 'SIGUNGU_NM']]
    final_df[area_cols] = final_df[area_cols].round(2)
    final_df['TOTAL_CHECK'] = final_df[area_cols].sum(axis=1)
    
    # 저장
    output_path = os.path.join(base_folder, 'Seoul_LandCover_Mapping.csv')
    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Saved to {output_path}")
    
    # 검증 출력 (강남구 2000년 데이터 확인)
    check = final_df[(final_df['SIGUNGU_NM'] == '강남구') & (final_df['YEAR'] == 2000)]
    print("\nVerification (Gangnam-gu 2000):")
    print(check.T)

if __name__ == "__main__":
    process_mixed_land_cover()
