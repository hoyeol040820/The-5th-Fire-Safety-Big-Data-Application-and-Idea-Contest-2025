import geopandas as gpd
import folium
import os

def test_boundary_display():
    """
    서울시 지도 위에 구경계와 동경계를 표시하는 테스트 함수
    """
    print("=== 서울시 행정구역 경계 표시 테스트 ===")
    
    # 파일 경로 설정
    boundary_dir = '../dataset/서울시_행정구역_경계'
    gu_file = os.path.join(boundary_dir, '서울시_구경계.shp')
    dong_file = os.path.join(boundary_dir, '서울시_동경계.shp')
    
    # 파일 존재 확인
    if not os.path.exists(gu_file):
        print(f"❌ 구경계 파일을 찾을 수 없습니다: {gu_file}")
        return
    if not os.path.exists(dong_file):
        print(f"❌ 동경계 파일을 찾을 수 없습니다: {dong_file}")
        return
    
    try:
        # 1. Shapefile 데이터 로드
        print("📂 Shapefile 데이터 로딩 중...")
        gu_gdf = gpd.read_file(gu_file, encoding='cp949')
        dong_gdf = gpd.read_file(dong_file, encoding='cp949')
        
        print(f"✅ 구경계 데이터: {len(gu_gdf)}개 구")
        print(f"✅ 동경계 데이터: {len(dong_gdf)}개 동")
        print(f"📍 구경계 좌표계: {gu_gdf.crs}")
        print(f"📍 동경계 좌표계: {dong_gdf.crs}")
        
        # 2. 좌표계 변환 (WGS84로 변환)
        print("🌐 좌표계를 WGS84로 변환 중...")
        gu_gdf = gu_gdf.to_crs('EPSG:4326')
        dong_gdf = dong_gdf.to_crs('EPSG:4326')
        
        # 3. 서울시 중심 좌표 계산
        bounds = gu_gdf.total_bounds  # [minx, miny, maxx, maxy]
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        
        print(f"📍 서울시 중심좌표: 위도 {center_lat:.4f}, 경도 {center_lon:.4f}")
        
        # 4. Folium 지도 생성
        print("🗺️  인터랙티브 지도 생성 중...")
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        # 5. 동경계 추가 (더 세밀한 경계)
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
        
        # 6. 구경계 추가 (굵은 경계선)
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
        
        # 7. 범례 추가
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 280px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:16px; padding: 15px">
        <p><b>서울시 행정구역 경계</b></p>
        <p><i class="fa fa-square" style="color:red"></i> 구경계 (25개구)</p>
        <p><i class="fa fa-square" style="color:blue"></i> 동경계 (426개동)</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 8. figure 폴더 생성 및 지도 저장
        figure_dir = '../figure'
        os.makedirs(figure_dir, exist_ok=True)
        
        output_file = os.path.join(figure_dir, 'test_서울시_행정구역_경계.html')
        m.save(output_file)
        
        print(f"✅ 지도 파일 저장 완료: {output_file}")
        print(f"🌐 브라우저에서 {output_file} 파일을 열어서 확인하세요!")
        
        # 9. 간단한 통계 출력
        print("\n=== 데이터 통계 ===")
        print(f"구 목록 (샘플): {', '.join(gu_gdf['SGG_NM'].str.replace('서울특별시 ', '').head(5).tolist())}...")
        print(f"동 목록 (샘플): {', '.join(dong_gdf['ADM_NM'].head(5).tolist())}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    # 테스트 실행
    success = test_boundary_display()
    if success:
        print("\n🎉 테스트 완료!")
    else:
        print("\n💥 테스트 실패!") 