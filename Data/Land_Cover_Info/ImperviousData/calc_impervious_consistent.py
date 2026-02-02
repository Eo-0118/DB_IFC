import pandas as pd
import os
import glob

def calculate_impervious_consistent(file_path):
    """
    모든 연도의 데이터를 Level 2 분류 체계 기준으로 일관되게 불투수 면적을 계산합니다.
    기준: 110, 120, 130, 140, 150, 160, 230 -> 불투수
          그 외 -> 투수
    """
    print(f"Processing {file_path}...")
    df = pd.read_csv(file_path)
    
    # 1. 시군구명 컬럼 확인
    sigungu_col = 'SIGUNGU_NM'
    if sigungu_col not in df.columns:
        print(f"  Skipping {file_path}: No SIGUNGU_NM column.")
        return

    # 2. 코드 컬럼 찾기 및 Level 2 코드 추출
    # L3_CODE, L2_CODE, LV2_CODE, CODE 중 하나를 사용
    code_col = None
    for col in ['L3_CODE', 'L2_CODE', 'LV2_CODE', 'CODE']:
        if col in df.columns:
            code_col = col
            break
            
    if not code_col:
        print(f"  Skipping {file_path}: No code column found.")
        return

    # 3. 일관된 LV2 코드 생성
    # L3_CODE인 경우 앞 2자리에 '0'을 붙여 110 형태의 LV2로 변환하거나, 
    # 기존 LV2 코드(110 등)를 정수형으로 처리
    def get_lv2_standard(code):
        try:
            code_str = str(int(code))
            if len(code_str) == 3:
                # 111, 112 같은 세분류면 110으로, 110 같은 중분류면 그대로 유지
                return int(code_str[:2] + '0')
            return int(code)
        except:
            return None

    df['LV2_CONSISTENT'] = df[code_col].apply(get_lv2_standard)

    # 4. 불투수 판별 (Level 2 기준 일괄 적용)
    # 110(주거), 120(공업), 130(상업), 140(문화체육), 150(교통), 160(공공), 230(시설재배)
    impervious_lv2 = {110, 120, 130, 140, 150, 160, 230}
    
    df['IS_IMPERVIOUS'] = df['LV2_CONSISTENT'].apply(lambda x: x in impervious_lv2 if x is not None else False)

    # 5. 시군구별 집계
    result = df.groupby(['SIGUNGU_NM', 'IS_IMPERVIOUS'])['AREA_M2'].sum().unstack(fill_value=0)
    
    # 컬럼 구조 안정화
    if True not in result.columns: result[True] = 0
    if False not in result.columns: result[False] = 0
    
    result = result.rename(columns={True: 'IMPERVIOUS_AREA_M2', False: 'PERVIOUS_AREA_M2'})
    
    # 6. 비율 계산
    result['TOTAL_AREA_M2'] = result['IMPERVIOUS_AREA_M2'] + result['PERVIOUS_AREA_M2']
    result['IMPERVIOUS_RATIO'] = (result['IMPERVIOUS_AREA_M2'] / result['TOTAL_AREA_M2'] * 100).fillna(0)
    
    result = result.reset_index()
    
    # 7. 파일 저장
    year = os.path.basename(file_path).split('_')[0]
    output_path = os.path.join(os.path.dirname(file_path), f"{year}_impervious_summary.csv")
    
    # 결과 저장 (BOM 포함하여 엑셀 가독성 유지)
    result.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"  Successfully saved to {output_path}")

def main():
    folder_path = '/Users/eoseungyun/Desktop/project/DB_IFC/Data/Land_Cover_Info/Seoul_Land_Cover'
    
    # 처리할 원본 파일 리스트 추출 (이미 생성된 impervious_summary는 제외)
    # _lv2_가 붙은 파일이든 아니든, 최신 가공된 요약본을 사용
    all_files = glob.glob(os.path.join(folder_path, '*_summary.csv'))
    
    # 연도별로 가장 적합한 파일 하나만 선택 (세분류가 있는 일반 summary 우선)
    year_to_file = {}
    for f in all_files:
        filename = os.path.basename(f)
        if 'impervious' in filename: continue
        
        year = filename.split('_')[0]
        # 일반 summary.csv가 있으면 그것을 사용 (세분류 정보가 있을 확률이 높으므로)
        # 만약 lv2_summary.csv만 있으면 그것을 사용
        if year not in year_to_file or 'lv2' in os.path.basename(year_to_file[year]):
            year_to_file[year] = f
            
    for year in sorted(year_to_file.keys()):
        calculate_impervious_consistent(year_to_file[year])

if __name__ == "__main__":
    main()
