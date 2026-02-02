import geopandas as gpd
import os
import glob

def main():
    # 1. 경로 설정
    base_dir = "/Users/eoseungyun/Desktop/project/DB_IFC/Data/Land_Cover_Info"
    input_dir = os.path.join(base_dir, "temp")
    sigungu_path = os.path.join(base_dir, "서울_시군구/bnd_sigungu_11_2025_2Q.shp")
    output_dir = os.path.join(base_dir, "Seoul_Land_Cover_Final")

    # 결과 저장 폴더 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"폴더 생성 완료: {output_dir}")

    # 2. 시군구 경계 데이터 로드
    print(f"시군구 경계 데이터를 불러오는 중: {os.path.basename(sigungu_path)}")
    sigungu_gdf = gpd.read_file(sigungu_path)
    # 시군구 데이터의 geometry 유효성 검사
    sigungu_gdf.geometry = sigungu_gdf.geometry.make_valid()
    
    # 3. temp 폴더 내의 병합된 shp 파일들 리스트업
    target_shps = glob.glob(os.path.join(input_dir, "*_add_area.shp"))
    # target_shps = glob.glob(os.path.join(input_dir, "*_lv2_add_area.shp"))
    print(f"교차 연산 대상 파일 수: {len(target_shps)}개")

    for shp_path in target_shps:
        target_name = os.path.basename(shp_path).replace("_add_area.shp", "")
        output_path = os.path.join(output_dir, f"{target_name}_intersected.shp")

        print(f"\n{'='*50}")
        print(f"[교차 연산 시작] 대상: {target_name}")

        try:
            # 땅피복 데이터 로드
            land_gdf = gpd.read_file(shp_path)
            if land_gdf.empty:
                print(f"  - {target_name}: 데이터가 비어 있어 건너뜁니다.")
                continue

            # 좌표계 일치 확인 (EPSG:5179)
            if land_gdf.crs != sigungu_gdf.crs:
                land_gdf = land_gdf.to_crs(sigungu_gdf.crs)

            # 4. 교차 연산 (Overlay Intersection)
            # land_gdf의 각 폴리곤을 sigungu_gdf 경계로 자름
            print(f"  - 공간 중첩(Intersection) 계산 중...")
            intersected_gdf = gpd.overlay(land_gdf, sigungu_gdf, how='intersection')

            if intersected_gdf.empty:
                print(f"  - {target_name}: 교차 영역 결과가 없습니다.")
                continue

            # 5. 잘려진 도형에 맞게 면적 재계산
            # 중첩되어 잘린 후의 실제 면적을 AREA_M2에 업데이트
            intersected_gdf['AREA_M2'] = intersected_gdf.geometry.area
            
            # 6. 결과 저장
            print(f"  - 결과 저장 중: {os.path.basename(output_path)}")
            intersected_gdf.to_file(output_path, encoding='utf-8')
            print(f"✅ 완료: {output_path}")

            # --- 요약 파일 생성  ---
            group_cols = ['SIGUNGU_NM']
            
            # 체크할 분류 단계 정의 (상세한 순서대로)
            lv3_candidates = ['L3_CODE', 'L3_NAME']
            lv2_candidates = ['L2_CODE', 'L2_NAME', 'LV2_CODE', 'LV2_NAME', 'CODE']
            lv1_candidates = ['L1_CODE', 'L1_NAME']
            # 1. 세분류(Level 3) 컬럼이 하나라도 있는지 확인
            found_l3 = [c for c in lv3_candidates if c in intersected_gdf.columns]
            if found_l3:
                group_cols.extend(found_l3)
            else:
                # 2. 세분류가 없으면 중분류(Level 2) 확인
                found_l2 = [c for c in lv2_candidates if c in intersected_gdf.columns]
                if found_l2:
                    group_cols.extend(found_l2)
                else:
                    # 3. 그마저도 없으면 대분류(Level 1) 확인
                    found_l1 = [c for c in lv1_candidates if c in intersected_gdf.columns]
                    group_cols.extend(found_l1)
                    
            # 필터링된 컬럼으로 그룹화
            summary = intersected_gdf.groupby(group_cols)['AREA_M2'].sum().reset_index()
            summary.to_csv(os.path.join(output_dir, f"{target_name}_summary.csv"), index=False, encoding='utf-8-sig')
            print(f"📊 요약 완료 ({len(group_cols)-1}단계 기준): {target_name}_summary.csv")


        except Exception as e:
            print(f"  - [에러 발생] {target_name}: {e}")

    print(f"\n{'='*50}")
    print("모든 공간 중첩 작업이 종료되었습니다.")

if __name__ == "__main__":
    main()
