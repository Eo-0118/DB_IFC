import pandas as pd
import os

def merge_land_info():
    # 스크립트 파일의 절대 경로를 구함
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 상위 폴더 (Land_Cover_Info)
    parent_dir = os.path.dirname(script_dir)

    base_folder = script_dir  # Seoul_Land_Cover 폴더
    impervious_folder = os.path.join(parent_dir, 'ImperviousData')
    
    # 1. 파일 경로 설정
    land_cover_path = os.path.join(base_folder, 'Seoul_LandCover_Mapping.csv')
    impervious_path = os.path.join(impervious_folder, 'Seoul_ImperviousData_2000_2024.csv')
    
    output_path = os.path.join(parent_dir, 'Seoul_Land_info.csv')
    
    if not os.path.exists(land_cover_path):
        print(f"Error: Land cover file not found at {land_cover_path}")
        return
    if not os.path.exists(impervious_path):
        print(f"Error: Impervious data file not found at {impervious_path}")
        return
        
    # 2. 데이터 로드
    print("Loading datasets...")
    lc_df = pd.read_csv(land_cover_path)
    imp_df = pd.read_csv(impervious_path)
    
    # 3. 데이터 병합 (YEAR, SIGUNGU_NM 기준)
    # imp_df에는 PERVIOUS_AREA_M2, IMPERVIOUS_AREA_M2, TOTAL_AREA_M2, IMPERVIOUS_RATIO가 있음
    # lc_df에는 주거지역, 공업지역... 등과 TOTAL_CHECK가 있음
    
    # 중복 컬럼 방지를 위해 imp_df에서 TOTAL_AREA_M2는 제외할 수도 있으나, 
    # 검증을 위해 유지하거나 비교 후 하나만 남길 수 있음.
    # 여기서는 모두 포함하고 접미사를 붙이지 않고 자연스럽게 병합 (컬럼명이 다르므로)
    # 단, TOTAL_AREA_M2 와 lc_df의 TOTAL_CHECK는 거의 같아야 함.
    
    print("Merging datasets...")
    merged_df = pd.merge(lc_df, imp_df, on=['YEAR', 'SIGUNGU_NM'], how='outer')
    
    # 컬럼 정리
    # lc_df의 TOTAL_CHECK는 제거 (imp_df의 TOTAL_AREA_M2 사용)
    if 'TOTAL_CHECK' in merged_df.columns:
        merged_df.drop(columns=['TOTAL_CHECK'], inplace=True)
        
    # 컬럼 순서 재배치 (가독성을 위해)
    # [YEAR, SIGUNGU] + [Land Cover cols] + [Impervious cols]
    
    # 기본 정보
    cols = ['YEAR', 'SIGUNGU_NM']
    
    # 토지피복 컬럼들 (기존 lc_df에서 가져옴)
    # 100번대(중분류) + 200~700(대분류)
    lc_cols = [c for c in lc_df.columns if c not in ['YEAR', 'SIGUNGU_NM', 'TOTAL_CHECK']]
    
    # 불투수시 정보 컬럼들 (순서 변경 요청 반영: Ratio -> Total Area)
    imp_cols = ['IMPERVIOUS_AREA_M2', 'PERVIOUS_AREA_M2', 'IMPERVIOUS_RATIO', 'TOTAL_AREA_M2']
    
    final_cols = cols + lc_cols + imp_cols
    
    # 사용 가능한 컬럼만 선택
    final_cols = [c for c in final_cols if c in merged_df.columns]
    
    final_df = merged_df[final_cols]
    
    # 4. 저장
    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Successfully saved merged file to {output_path}")
    print(final_df.head())

if __name__ == "__main__":
    merge_land_info()
