# -*- coding: utf-8 -*-
import geopandas as gpd
import folium
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

def create_vulnerable_population_heatmap():
    """
    구별 재난안전취약자 밀도(면적 대비) 히트맵 생성
    """
    print("🚨 재난안전취약자 밀도 히트맵 생성 시작...")
    
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
        
        # 재난안전취약자 정보 데이터
        vulnerable_df = pd.read_csv('dataset/4_select_feature/재난안전취약자정보_selected_features.csv')
        print(f"✅ 재난안전취약자 데이터: {len(vulnerable_df)}개 구역")
        print("재난안전취약자 데이터 샘플:")
        print(vulnerable_df.head())
        
        # 2. 구로구, 금천구 분리 처리
        print("\n🔧 구로구, 금천구 데이터 분리 처리 중...")
        guro_geumcheon_row = vulnerable_df[vulnerable_df['관할구역명'] == '구로구, 금천구'].iloc[0]
        
        if len(guro_geumcheon_row) > 0:
            # 구로구, 금천구 데이터를 각각 절반씩 분배 (단순 분배)
            guro_data = guro_geumcheon_row.copy()
            guro_data['관할구역명'] = '구로구'
            guro_data['독거노인가구수'] = int(guro_data['독거노인가구수'] * 0.6)  # 구로구가 더 큼
            guro_data['고령인구수'] = int(guro_data['고령인구수'] * 0.6)
            guro_data['유아인구수'] = int(guro_data['유아인구수'] * 0.6)
            guro_data['등록장애인수'] = int(guro_data['등록장애인수'] * 0.6)
            guro_data['1인가구수'] = int(guro_data['1인가구수'] * 0.6)
            guro_data['관할면적'] = 20.12  # 구로구 면적
            
            geumcheon_data = guro_geumcheon_row.copy()
            geumcheon_data['관할구역명'] = '금천구'
            geumcheon_data['독거노인가구수'] = int(guro_geumcheon_row['독거노인가구수'] * 0.4)  # 금천구가 더 작음
            geumcheon_data['고령인구수'] = int(guro_geumcheon_row['고령인구수'] * 0.4)
            geumcheon_data['유아인구수'] = int(guro_geumcheon_row['유아인구수'] * 0.4)
            geumcheon_data['등록장애인수'] = int(guro_geumcheon_row['등록장애인수'] * 0.4)
            geumcheon_data['1인가구수'] = int(guro_geumcheon_row['1인가구수'] * 0.4)
            geumcheon_data['관할면적'] = 13.02  # 금천구 면적
            
            # 원본 행 제거하고 분리된 데이터 추가
            vulnerable_df = vulnerable_df[vulnerable_df['관할구역명'] != '구로구, 금천구'].copy()
            vulnerable_df = pd.concat([vulnerable_df, pd.DataFrame([guro_data]), pd.DataFrame([geumcheon_data])], ignore_index=True)
            print(f"✅ 구로구, 금천구 분리 완료 → 총 {len(vulnerable_df)}개 구")
        
        # 3. 취약자 밀도 계산
        print("\n🧮 재난안전취약자 밀도 계산 중...")
        vulnerable_df['총취약자수'] = (
            vulnerable_df['독거노인가구수'] + 
            vulnerable_df['고령인구수'] + 
            vulnerable_df['유아인구수'] + 
            vulnerable_df['등록장애인수'] + 
            vulnerable_df['1인가구수']
        )
        
        vulnerable_df['취약자밀도'] = vulnerable_df['총취약자수'] / vulnerable_df['관할면적']
        
        print("취약자 밀도 상위 5개:")
        print(vulnerable_df.nlargest(5, '취약자밀도')[['관할구역명', '취약자밀도', '총취약자수', '관할면적']])
        
        # 4. 구명 정리 (매칭을 위해)
        print("\n🔗 데이터 매칭 준비 중...")
        vulnerable_df['구명'] = vulnerable_df['관할구역명'].str.replace('구', '')
        gu_boundary['구명_clean'] = gu_boundary['구명'].str.replace('구', '')
        
        # 5. Min-Max Scaling
        print("\n⚖️ Min-Max Scaling 적용 중...")
        scaler = MinMaxScaler()
        vulnerable_df['밀도_normalized'] = scaler.fit_transform(vulnerable_df[['취약자밀도']]).flatten()
        
        print(f"정규화 결과:")
        print(f"원본 밀도 범위: {vulnerable_df['취약자밀도'].min():.2f} ~ {vulnerable_df['취약자밀도'].max():.2f}")
        print(f"정규화 범위: {vulnerable_df['밀도_normalized'].min():.2f} ~ {vulnerable_df['밀도_normalized'].max():.2f}")
        
        # 6. 경계 데이터와 병합
        print("\n🗺️ 지도 데이터 병합 중...")
        gu_merged = gu_boundary.merge(vulnerable_df, left_on='구명_clean', right_on='구명', how='left')
        print(f"지도 데이터 병합 결과: {len(gu_merged)}개 구")
        
        # 7. 서울시 중심 좌표 계산
        bounds = gu_boundary.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        print(f"📍 서울시 중심좌표: 위도 {center_lat:.4f}, 경도 {center_lon:.4f}")
        
        # 8. 색상 함수 정의
        def get_color(value):
            """정규화된 값에 따른 색상 반환 (취약자 밀도용 빨간색 계열)"""
            if pd.isna(value):
                return '#CCCCCC'  # 회색 (데이터 없음)
            
            # 0-1 범위의 값을 색상으로 변환 (빨간색 계열)
            if value <= 0.2:
                return '#FFE5E5'  # 연한 빨간색
            elif value <= 0.4:
                return '#FFB3B3'  # 밝은 빨간색
            elif value <= 0.6:
                return '#FF8080'  # 중간 빨간색
            elif value <= 0.8:
                return '#FF4D4D'  # 진한 빨간색
            else:
                return '#CC0000'  # 매우 진한 빨간색
        
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
        
        # 11. 구별 재난안전취약자 밀도 히트맵 추가
        print("구별 재난안전취약자 밀도 히트맵 추가...")
        
        for idx, row in gu_merged.iterrows():
            density_normalized = row.get('밀도_normalized', np.nan)
            fill_color = get_color(density_normalized)
            
            # 구 경계에 색상 적용
            folium.GeoJson(
                row.geometry,
                style_function=lambda x, color=fill_color: {
                    'fillColor': color,
                    'color': '#8B0000',  # 어두운 빨간색 테두리
                    'weight': 2,
                    'opacity': 0.8,
                    'fillOpacity': 0.7
                },
                popup=folium.Popup(
                    f"""
                    <div style="font-family: Arial; padding: 10px; width: 280px;">
                    <h4 style="margin: 0; color: #8B0000;">🚨 {row.get('관할구역명', 'N/A')}</h4>
                    <hr style="margin: 5px 0;">
                    <p><strong>📊 취약자 밀도:</strong> {row.get('취약자밀도', 0):.2f} 명/km²</p>
                    <p><strong>📈 정규화 값:</strong> {row.get('밀도_normalized', 0):.3f}</p>
                    <p><strong>👥 총 취약자수:</strong> {row.get('총취약자수', 0):,.0f} 명</p>
                    <p><strong>📐 관할 면적:</strong> {row.get('관할면적', 0):.2f} km²</p>
                    <hr style="margin: 5px 0;">
                    <div style="font-size: 11px; color: #666;">
                    <p><strong>세부 구성:</strong></p>
                    <p>👴 독거노인: {row.get('독거노인가구수', 0):,}가구</p>
                    <p>🧓 고령인구: {row.get('고령인구수', 0):,}명</p>
                    <p>👶 유아인구: {row.get('유아인구수', 0):,}명</p>
                    <p>♿ 등록장애인: {row.get('등록장애인수', 0):,}명</p>
                    <p>🏠 1인가구: {row.get('1인가구수', 0):,}가구</p>
                    </div>
                    </div>
                    """,
                    max_width=320
                ),
                tooltip=f"{row.get('관할구역명', 'N/A')}: {row.get('취약자밀도', 0):.0f} 명/km²"
            ).add_to(m)
        
        # 12. 범례 추가
        print("범례 추가...")
        legend_html = '''
        <div style="position: fixed; top: 10px; right: 10px; width: 340px; 
                    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,249,250,0.95));
                    border: none; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                    backdrop-filter: blur(10px); padding: 20px; font-family: Arial; z-index: 9999;">
        
        <h3 style="margin: 0 0 15px 0; text-align: center; color: #8B0000; font-size: 18px;">
            🚨 재난안전취약자 밀도 분석
        </h3>
        
        <div style="margin-bottom: 15px;">
            <p style="margin: 5px 0; font-weight: 600; color: #8B0000;">📊 밀도 계산 공식:</p>
            <div style="background: #FFF5F5; padding: 10px; border-radius: 8px; font-size: 11px; color: #8B0000;">
                (독거노인 + 고령인구 + 유아인구 + 등록장애인 + 1인가구) ÷ 관할면적
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <p style="margin: 5px 0; font-weight: 600; color: #8B0000;">🎨 색상 범례:</p>
            <div style="display: flex; flex-direction: column; gap: 5px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #FFE5E5; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">매우 낮음 (0.0~0.2)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #FFB3B3; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">낮음 (0.2~0.4)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #FF8080; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">보통 (0.4~0.6)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #FF4D4D; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">높음 (0.6~0.8)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #CC0000; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">매우 높음 (0.8~1.0)</span>
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <p style="margin: 5px 0; font-weight: 600; color: #8B0000;">👥 취약자 구성:</p>
            <div style="font-size: 11px; color: #666; line-height: 1.4;">
                👴 독거노인가구 + 🧓 고령인구 + 👶 유아인구<br>
                + ♿ 등록장애인 + 🏠 1인가구
            </div>
        </div>
        
        <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #FFB3B3, transparent); margin: 15px 0;">
        
        <div style="text-align: center;">
            <div style="font-size: 11px; color: #8B0000; margin-bottom: 5px;">
                🚨 재난 대응 취약계층 밀도 분석
            </div>
            <div style="font-size: 11px; color: #666; margin-bottom: 5px;">
                📊 Min-Max 정규화 적용
            </div>
            <div style="font-size: 10px; color: #999;">
                🔴 색상이 진할수록 취약자 밀도가 높음
            </div>
        </div>
        
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 13. 지도 저장
        output_file = 'figure/재난안전취약자_히트맵.html'
        m.save(output_file)
        
        print(f"\n✅ 재난안전취약자 밀도 히트맵 생성 완료!")
        print(f"📁 저장 위치: {output_file}")
        
        # 14. 통계 요약 출력
        print(f"\n📊 분석 결과 요약:")
        print(f"전체 구 수: {len(vulnerable_df)}개")
        print(f"평균 취약자 밀도: {vulnerable_df['취약자밀도'].mean():.2f} 명/km²")
        print(f"최대 취약자 밀도: {vulnerable_df['취약자밀도'].max():.2f} 명/km²")
        print(f"최소 취약자 밀도: {vulnerable_df['취약자밀도'].min():.2f} 명/km²")
        
        print(f"\n🔝 취약자 밀도 상위 10개 구:")
        top_vulnerable = vulnerable_df.nlargest(10, '취약자밀도')[
            ['관할구역명', '취약자밀도', '총취약자수', '관할면적', '밀도_normalized']
        ]
        for idx, row in top_vulnerable.iterrows():
            print(f"  {row['관할구역명']}: {row['취약자밀도']:.2f} 명/km² "
                  f"(총취약자: {row['총취약자수']:,.0f}명, 면적: {row['관할면적']:.2f}km², 정규화: {row['밀도_normalized']:.3f})")
        
        # 15. 취약자 구성별 통계
        print(f"\n👥 취약자 구성별 평균:")
        print(f"👴 독거노인가구: {vulnerable_df['독거노인가구수'].mean():.0f}가구")
        print(f"🧓 고령인구: {vulnerable_df['고령인구수'].mean():.0f}명")
        print(f"👶 유아인구: {vulnerable_df['유아인구수'].mean():.0f}명")
        print(f"♿ 등록장애인: {vulnerable_df['등록장애인수'].mean():.0f}명")
        print(f"🏠 1인가구: {vulnerable_df['1인가구수'].mean():.0f}가구")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_vulnerable_population_heatmap()
    if success:
        print("\n🎉 재난안전취약자 밀도 히트맵 생성 완료!")
    else:
        print("\n💥 히트맵 생성 실패!") 