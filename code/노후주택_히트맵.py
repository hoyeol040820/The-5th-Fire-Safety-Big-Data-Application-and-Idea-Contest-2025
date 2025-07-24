# -*- coding: utf-8 -*-
import geopandas as gpd
import folium
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

def create_aging_housing_density_heatmap():
    """
    구별 노후 주택 밀도(면적 대비) 히트맵 생성 - 소계 값 사용
    """
    print("🏠 노후 주택 밀도 히트맵 생성 시작... (소계 값 사용)")
    
    try:
        # 1. 데이터 로드
        print("\n📂 데이터 로딩 중...")
        
        # 구 경계 데이터
        gu_boundary = gpd.read_file('dataset/서울시_행정구역_경계/서울시_구경계.shp', encoding='cp949')
        gu_boundary = gu_boundary.to_crs('EPSG:4326')
        gu_boundary['구명'] = gu_boundary['SGG_NM'].str.replace('서울특별시 ', '')
        print(f"✅ 구 경계 데이터: {len(gu_boundary)}개 구")
        
        # 동 경계 데이터
        dong_boundary = gpd.read_file('dataset/서울시_행정구역_경계/서울시_동경계.shp', encoding='cp949')
        dong_boundary = dong_boundary.to_crs('EPSG:4326')
        
        # 구 매핑을 위한 코드
        gu_code_mapping = {
            '11010': '종로구', '11020': '중구', '11030': '용산구', '11040': '성동구',
            '11050': '광진구', '11060': '동대문구', '11070': '중랑구', '11080': '성북구',
            '11090': '강북구', '11100': '도봉구', '11110': '노원구', '11120': '은평구',
            '11130': '서대문구', '11140': '마포구', '11150': '양천구', '11160': '강서구',
            '11170': '구로구', '11180': '금천구', '11190': '영등포구', '11200': '동작구',
            '11210': '관악구', '11220': '서초구', '11230': '강남구', '11240': '송파구',
            '11250': '강동구'
        }
        dong_boundary['구코드'] = dong_boundary['ADM_CD'].str[:5]
        dong_boundary['구명'] = dong_boundary['구코드'].map(gu_code_mapping)
        dong_boundary['동명'] = dong_boundary['ADM_NM']
        print(f"✅ 동 경계 데이터: {len(dong_boundary)}개 동")
        
        # 노후 주택 현황 데이터
        housing_df = pd.read_csv('dataset/4_select_feature/노후기간별_주택현황_selected_features.csv')
        housing_df = housing_df[housing_df['구명'] != '소계'].copy()
        print(f"✅ 노후 주택 데이터: {len(housing_df)}개 구")
        print("노후 주택 데이터 샘플:")
        print(housing_df.head())
        
        # 면적 데이터 - ✅ 소계 값만 사용
        area_df = pd.read_csv('dataset/4_select_feature/서울시_행정구역(동별)_면적.csv')
        print(f"전체 면적 데이터: {len(area_df)}개 행")
        
        # ✅ 소계 행만 선택하여 구별 면적 추출
        gu_area = area_df[area_df['동명'] == '소계'][['구명', '면적_km2']].copy()
        gu_area.columns = ['구명', '총면적_km2']
        print(f"✅ 구별 면적 데이터 (소계 사용): {len(gu_area)}개 구")
        print("구별 면적 상위 5개:")
        print(gu_area.nlargest(5, '총면적_km2'))
        
        # 2. 노후 주택 가중치 계산
        print("\n🏠 노후 주택 가중치 계산 중...")
        housing_df['weighted_old_housing'] = (
            housing_df['30년이상_주택수'] * 1.5 + 
            housing_df['20년~30년미만_주택수']
        )
        print("가중 노후 주택수 상위 5개:")
        print(housing_df.nlargest(5, 'weighted_old_housing')[['구명', 'weighted_old_housing', '30년이상_주택수', '20년~30년미만_주택수']])
        
        # 3. 데이터 병합
        print("\n🔗 데이터 병합 중...")
        # 구명에서 '구' 제거하여 매칭
        housing_df['구명_clean'] = housing_df['구명'].str.replace('구', '')
        gu_area['구명_clean'] = gu_area['구명'].str.replace('구', '')
        
        merged_data = pd.merge(housing_df, gu_area, on='구명_clean', how='inner')
        print(f"병합 결과: {len(merged_data)}개 구")
        
        # 4. 밀도 계산 (가중 노후주택수 / 면적)
        print("\n📊 노후 주택 밀도 계산 중...")
        merged_data['housing_density'] = merged_data['weighted_old_housing'] / merged_data['총면적_km2']
        print("노후 주택 밀도 상위 5개:")
        print(merged_data.nlargest(5, 'housing_density')[['구명_x', 'housing_density', 'weighted_old_housing', '총면적_km2']])
        
        # 5. Min-Max Scaling
        print("\n⚖️ Min-Max Scaling 적용 중...")
        scaler = MinMaxScaler()
        merged_data['density_normalized'] = scaler.fit_transform(merged_data[['housing_density']]).flatten()
        
        print(f"정규화 결과:")
        print(f"원본 밀도 범위: {merged_data['housing_density'].min():.2f} ~ {merged_data['housing_density'].max():.2f}")
        print(f"정규화 범위: {merged_data['density_normalized'].min():.2f} ~ {merged_data['density_normalized'].max():.2f}")
        
        # 6. 경계 데이터와 병합
        print("\n🗺️ 지도 데이터 병합 중...")
        gu_boundary['구명_clean'] = gu_boundary['구명'].str.replace('구', '')
        gu_merged = gu_boundary.merge(merged_data, left_on='구명_clean', right_on='구명_clean', how='left')
        print(f"지도 데이터 병합 결과: {len(gu_merged)}개 구")
        
        # 7. 서울시 중심 좌표 계산
        bounds = gu_boundary.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        print(f"📍 서울시 중심좌표: 위도 {center_lat:.4f}, 경도 {center_lon:.4f}")
        
        # 8. 색상 함수 정의
        def get_color(value):
            """정규화된 값에 따른 색상 반환"""
            if pd.isna(value):
                return '#CCCCCC'  # 회색 (데이터 없음)
            
            # 0-1 범위의 값을 색상으로 변환
            if value <= 0.2:
                return '#FFF5B7'  # 연한 노란색
            elif value <= 0.4:
                return '#FFD93D'  # 노란색
            elif value <= 0.6:
                return '#FF8A00'  # 주황색
            elif value <= 0.8:
                return '#FF4500'  # 빨간 주황색
            else:
                return '#DC143C'  # 진한 빨간색
        
        # 9. Folium 지도 생성
        print("\n🗺️ 인터랙티브 지도 생성 중...")
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='CartoDB positron'
        )
        
        # 10. 동 경계 추가 (배경)
        print("동 경계 추가...")
        folium.GeoJson(
            dong_boundary.to_json(),
            style_function=lambda feature: {
                'fillColor': 'none',
                'color': '#B0B0B0',
                'weight': 0.5,
                'opacity': 0.5,
                'fillOpacity': 0
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['구명', '동명'], 
                aliases=['구:', '동:']
            )
        ).add_to(m)
        
        # 11. 구별 노후 주택 밀도 히트맵 추가
        print("구별 노후 주택 밀도 히트맵 추가...")
        
        for idx, row in gu_merged.iterrows():
            density_normalized = row.get('density_normalized', np.nan)
            fill_color = get_color(density_normalized)
            
            # 구 경계에 색상 적용
            folium.GeoJson(
                row.geometry,
                style_function=lambda x, color=fill_color: {
                    'fillColor': color,
                    'color': '#2C3E50',
                    'weight': 2,
                    'opacity': 0.8,
                    'fillOpacity': 0.7
                },
                popup=folium.Popup(
                    f"""
                    <div style="font-family: Arial; padding: 10px; width: 250px;">
                    <h4 style="margin: 0; color: #2C3E50;">🏠 {row.get('구명', 'N/A')}</h4>
                    <hr style="margin: 5px 0;">
                    <p><strong>📊 노후주택 밀도:</strong> {row.get('housing_density', 0):.2f} 호/km²</p>
                    <p><strong>📈 정규화 값:</strong> {row.get('density_normalized', 0):.3f}</p>
                    <p><strong>🏘️ 가중 노후주택:</strong> {row.get('weighted_old_housing', 0):,.0f} 호</p>
                    <p><strong>📐 총 면적 (소계):</strong> {row.get('총면적_km2', 0):.2f} km²</p>
                    <hr style="margin: 5px 0;">
                    <p style="font-size: 11px; color: #7F8C8D;">
                    30년이상(×1.5) + 20~30년 미만 주택수<br>
                    ✅ 공식 소계 면적 사용
                    </p>
                    </div>
                    """,
                    max_width=300
                ),
                tooltip=f"{row.get('구명', 'N/A')}: {row.get('housing_density', 0):.2f} 호/km²"
            ).add_to(m)
        
        # 12. 범례 추가
        print("범례 추가...")
        legend_html = '''
        <div style="position: fixed; top: 10px; right: 10px; width: 320px; 
                    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,249,250,0.95));
                    border: none; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                    backdrop-filter: blur(10px); padding: 20px; font-family: Arial; z-index: 9999;">
        
        <h3 style="margin: 0 0 15px 0; text-align: center; color: #2C3E50; font-size: 18px;">
            🏠 노후 주택 밀도 분석 (소계 사용)
        </h3>
        
        <div style="margin-bottom: 15px;">
            <p style="margin: 5px 0; font-weight: 600; color: #2C3E50;">📊 밀도 계산 공식:</p>
            <div style="background: #F8F9FA; padding: 10px; border-radius: 8px; font-size: 12px; color: #495057;">
                (30년이상 주택수 × 1.5 + 20~30년 주택수) ÷ 구 면적(소계)
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <p style="margin: 5px 0; font-weight: 600; color: #2C3E50;">🎨 색상 범례:</p>
            <div style="display: flex; flex-direction: column; gap: 5px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #FFF5B7; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">매우 낮음 (0.0~0.2)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #FFD93D; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">낮음 (0.2~0.4)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #FF8A00; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">보통 (0.4~0.6)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #FF4500; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">높음 (0.6~0.8)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #DC143C; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">매우 높음 (0.8~1.0)</span>
                </div>
            </div>
        </div>
        
        <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #BDC3C7, transparent); margin: 15px 0;">
        
        <div style="text-align: center;">
            <div style="font-size: 11px; color: #7F8C8D; margin-bottom: 5px;">
                ✅ 공식 소계 면적 사용으로 정확도 향상
            </div>
            <div style="font-size: 11px; color: #7F8C8D; margin-bottom: 5px;">
                📊 Min-Max 정규화 적용
            </div>
            <div style="font-size: 10px; color: #95A5A6;">
                🔥 색상이 진할수록 노후주택 밀도가 높음
            </div>
        </div>
        
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 13. 지도 저장
        output_file = 'figure/노후주택_히트맵.html'
        m.save(output_file)
        
        print(f"\n✅ 노후 주택 밀도 히트맵 생성 완료!")
        print(f"📁 저장 위치: {output_file}")
        
        # 14. 통계 요약 출력 및 비교
        print(f"\n📊 분석 결과 요약 (소계 사용):")
        print(f"전체 구 수: {len(merged_data)}개")
        print(f"평균 노후주택 밀도: {merged_data['housing_density'].mean():.2f} 호/km²")
        print(f"최대 노후주택 밀도: {merged_data['housing_density'].max():.2f} 호/km²")
        print(f"최소 노후주택 밀도: {merged_data['housing_density'].min():.2f} 호/km²")
        
        print(f"\n🔝 노후주택 밀도 상위 10개 구:")
        top_density = merged_data.nlargest(10, 'housing_density')[
            ['구명_x', 'housing_density', 'weighted_old_housing', '총면적_km2', 'density_normalized']
        ]
        for idx, row in top_density.iterrows():
            print(f"  {row['구명_x']}: {row['housing_density']:.2f} 호/km² "
                  f"(가중주택: {row['weighted_old_housing']:,.0f}호, 면적: {row['총면적_km2']:.2f}km², 정규화: {row['density_normalized']:.3f})")
        
        # 15. 면적 데이터 검증 정보 출력
        print(f"\n✅ 면적 데이터 검증:")
        print("- 동명이 '소계'인 공식 구별 면적 사용")
        print("- 반올림 및 측량 정밀도가 고려된 공식 통계값")
        print("- 행정구역 통계 표준 방식 적용")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_aging_housing_density_heatmap()
    if success:
        print("\n🎉 노후 주택 밀도 히트맵 생성 완료!")
    else:
        print("\n💥 히트맵 생성 실패!") 