# -*- coding: utf-8 -*-
import geopandas as gpd
import folium
import pandas as pd
import os
from folium.plugins import HeatMap
import numpy as np

def test_coordinate_mapping():
    """
    서울시 지도 위에 구경계, 동경계와 함께 구조출동 좌표를 표시하는 테스트 함수
    """
    print("=== 서울시 구조출동 좌표 지도 매핑 테스트 ===")
    
    # 파일 경로 설정
    boundary_dir = '../dataset/서울시_행정구역_경계'
    gu_file = os.path.join(boundary_dir, '서울시_구경계.shp')
    dong_file = os.path.join(boundary_dir, '서울시_동경계.shp')
    coord_file = '../dataset/4_select_feature/서울시_구조출동_selected_features.csv'
    
    # 파일 존재 확인
    if not os.path.exists(gu_file):
        print(f"❌ 구경계 파일을 찾을 수 없습니다: {gu_file}")
        return
    if not os.path.exists(dong_file):
        print(f"❌ 동경계 파일을 찾을 수 없습니다: {dong_file}")
        return
    if not os.path.exists(coord_file):
        print(f"❌ 구조출동 데이터를 찾을 수 없습니다: {coord_file}")
        return
    
    try:
        # 1. Shapefile 데이터 로드
        print("📂 Shapefile 데이터 로딩 중...")
        gu_gdf = gpd.read_file(gu_file, encoding='cp949')
        dong_gdf = gpd.read_file(dong_file, encoding='cp949')
        
        print(f"✅ 구경계 데이터: {len(gu_gdf)}개 구")
        print(f"✅ 동경계 데이터: {len(dong_gdf)}개 동")
        
        # 2. 구조출동 좌표 데이터 로드
        print("📂 구조출동 좌표 데이터 로딩 중...")
        coord_df = pd.read_csv(coord_file, encoding='utf-8-sig')
        print(f"✅ 구조출동 데이터: {len(coord_df):,}개 레코드")
        
        # 3. 좌표 데이터 전처리
        print("🔧 좌표 데이터 전처리 중...")
        # 좌표 유효성 검사
        valid_coord_mask = (
            (coord_df['피해지역_경도'].notna()) & 
            (coord_df['피해지역_위도'].notna()) &
            (coord_df['피해지역_경도'] != 0) &
            (coord_df['피해지역_위도'] != 0) &
            (coord_df['피해지역_경도'] > 126) &
            (coord_df['피해지역_경도'] < 128) &
            (coord_df['피해지역_위도'] > 37) &
            (coord_df['피해지역_위도'] < 38)
        )
        
        coord_df_valid = coord_df[valid_coord_mask].copy()
        print(f"✅ 유효한 좌표 데이터: {len(coord_df_valid):,}개 레코드")
        
        # 4. 좌표계 변환 (WGS84로 변환)
        print("🌐 좌표계를 WGS84로 변환 중...")
        gu_gdf = gu_gdf.to_crs('EPSG:4326')
        dong_gdf = dong_gdf.to_crs('EPSG:4326')
        
        # 5. 서울시 중심 좌표 계산
        bounds = gu_gdf.total_bounds  # [minx, miny, maxx, maxy]
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        
        print(f"📍 서울시 중심좌표: 위도 {center_lat:.4f}, 경도 {center_lon:.4f}")
        
        # 6. Folium 지도 생성
        print("🗺️  인터랙티브 지도 생성 중...")
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        # 7. 동경계 추가 (더 세밀한 경계)
        print("📍 동경계 추가 중...")
        folium.GeoJson(
            dong_gdf.to_json(),
            style_function=lambda feature: {
                'fillColor': 'lightblue',
                'color': 'blue',
                'weight': 1,
                'fillOpacity': 0.1,
                'opacity': 0.8
            },
            popup=folium.GeoJsonPopup(fields=['ADM_NM'], aliases=['동명:']),
            tooltip=folium.GeoJsonTooltip(fields=['ADM_NM'], aliases=['동명:'])
        ).add_to(m)
        
        # 8. 구경계 추가 (굵은 경계선)
        print("📍 구경계 추가 중...")
        folium.GeoJson(
            gu_gdf.to_json(),
            style_function=lambda feature: {
                'fillColor': 'none',
                'color': 'red',
                'weight': 3,
                'fillOpacity': 0,
                'opacity': 1.0
            },
            popup=folium.GeoJsonPopup(fields=['SGG_NM'], aliases=['구명:']),
            tooltip=folium.GeoJsonTooltip(fields=['SGG_NM'], aliases=['구명:'])
        ).add_to(m)
        
        # 9. 구조출동 좌표를 HeatMap으로 추가
        print("🚒 구조출동 히트맵 생성 중...")
        
        # HeatMap용 데이터 준비 (위도, 경도 순서)
        heat_data = []
        for idx, row in coord_df_valid.iterrows():
            lat = row['피해지역_위도']
            lon = row['피해지역_경도']
            # 좌표값이 숫자인지 확인
            if pd.notna(lat) and pd.notna(lon) and isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                heat_data.append([float(lat), float(lon)])
        
        print(f"✅ 히트맵 데이터 포인트: {len(heat_data):,}개")
        
        # HeatMap 생성 (파라미터 단순화)
        HeatMap(
            heat_data,
            min_opacity=0.2,
            radius=15,
            blur=10
        ).add_to(m)
        
        # 10. 범례 추가
        legend_html = f'''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 300px; height: 220px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 15px; overflow-y: auto;">
        <p><b>서울시 구조출동 히트맵</b></p>
        <p><i class="fa fa-square" style="color:red"></i> 구경계 (25개구)</p>
        <p><i class="fa fa-square" style="color:blue"></i> 동경계 (426개동)</p>
        <hr>
        <p><b>구조출동 밀도 ({len(heat_data):,}개 데이터)</b></p>
        <div style="background: linear-gradient(to right, blue, cyan, lime, yellow, orange, red); 
                    height: 20px; width: 200px; margin: 10px 0;"></div>
        <div style="display: flex; justify-content: space-between; width: 200px; font-size: 12px;">
            <span>낮음</span>
            <span>높음</span>
        </div>
        <p style="margin-top: 10px; font-size: 12px;">
        🔵 파란색: 낮은 밀도<br>
        🟡 노란색: 중간 밀도<br>
        🔴 빨간색: 높은 밀도
        </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 11. 레이어 컨트롤 추가
        folium.LayerControl().add_to(m)
        
        # 12. figure 폴더 생성 및 지도 저장
        figure_dir = '../figure'
        os.makedirs(figure_dir, exist_ok=True)
        
        output_file = os.path.join(figure_dir, '구조출동_좌표_히트맵.html')
        m.save(output_file)
        
        print(f"✅ 지도 파일 저장 완료: {output_file}")
        print(f"🌐 브라우저에서 {output_file} 파일을 열어서 확인하세요!")
        
        # 13. 데이터 통계 출력
        print("\n=== 데이터 통계 ===")
        print(f"📊 전체 구조출동 데이터: {len(coord_df):,}개")
        print(f"📊 유효한 좌표 데이터: {len(coord_df_valid):,}개")
        print(f"📊 히트맵에 표시된 데이터: {len(heat_data):,}개")
        
        # 처리결과별 통계
        print("\n=== 처리결과별 통계 ===")
        result_stats = coord_df_valid['처리결과_구분명'].value_counts()
        for result, count in result_stats.head(10).items():
            print(f"  {result}: {count:,}건")
        
        # 구별 통계
        print("\n=== 구별 상위 10개 지역 ===")
        gu_stats = coord_df_valid['발생지역_시군구명'].value_counts()
        for gu, count in gu_stats.head(10).items():
            print(f"  {gu}: {count:,}건")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 테스트 실행
    success = test_coordinate_mapping()
    if success:
        print("\n🎉 테스트 완료!")
    else:
        print("\n💥 테스트 실패!") 