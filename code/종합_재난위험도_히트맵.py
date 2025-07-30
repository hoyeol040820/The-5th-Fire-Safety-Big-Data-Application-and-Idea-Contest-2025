# -*- coding: utf-8 -*-
import geopandas as gpd
import folium
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import warnings
import os
warnings.filterwarnings('ignore')

def create_comprehensive_disaster_risk_heatmap():
    """
    4개 히트맵 데이터를 종합한 재난 위험도 히트맵 생성
    - 재난안전취약자: 0.3 가중치
    - 취약연령: 0.3 가중치  
    - 노후주택: 0.2 가중치
    - 구조출동: 0.2 가중치
    """
    print("🚨 종합 재난 위험도 히트맵 생성 시작...")
    
    try:
        # 1. 기본 지리 데이터 로드
        print("\n📂 기본 지리 데이터 로딩 중...")
        
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
        
        # 2. 각 히트맵 데이터 추출 및 처리
        print("\n📊 각 히트맵 데이터 추출 중...")
        
        # === 2.1 취약연령 데이터 (동별) ===
        print("👶🧓 취약연령 데이터 처리 중...")
        population_df = pd.read_csv('dataset/4_select_feature/서울시_등록인구_2025_1분기_동별_최종.csv')
        area_df = pd.read_csv('dataset/4_select_feature/서울시_행정구역(동별)_면적.csv')
        area_df = area_df[area_df['동명'] != '소계'].copy()
        
        # 취약연령층 인구 계산
        population_df['취약연령인구'] = population_df['0~14세'] + population_df['65~']
        
        # 데이터 병합 (인구 + 면적)
        vulnerable_age_data = pd.merge(
            population_df, 
            area_df[['구명', '동명', '면적_km2']], 
            left_on=['구', '동'], 
            right_on=['구명', '동명'], 
            how='inner'
        )
        
        # 밀도 계산
        vulnerable_age_data['취약연령밀도'] = vulnerable_age_data['취약연령인구'] / vulnerable_age_data['면적_km2']
        print(f"✅ 취약연령 데이터: {len(vulnerable_age_data)}개 동")
        
        # === 2.2 재난안전취약자 데이터 (구별) ===
        print("🚨 재난안전취약자 데이터 처리 중...")
        vulnerable_df = pd.read_csv('dataset/4_select_feature/재난안전취약자정보_selected_features.csv')
        
        # 구로구, 금천구 분리 처리
        guro_geumcheon_row = vulnerable_df[vulnerable_df['관할구역명'] == '구로구, 금천구']
        if len(guro_geumcheon_row) > 0:
            guro_geumcheon_row = guro_geumcheon_row.iloc[0]
            
            # 구로구 데이터
            guro_data = guro_geumcheon_row.copy()
            guro_data['관할구역명'] = '구로구'
            guro_data['독거노인가구수'] = int(guro_data['독거노인가구수'] * 0.6)
            guro_data['고령인구수'] = int(guro_data['고령인구수'] * 0.6)
            guro_data['유아인구수'] = int(guro_data['유아인구수'] * 0.6)
            guro_data['등록장애인수'] = int(guro_data['등록장애인수'] * 0.6)
            guro_data['1인가구수'] = int(guro_data['1인가구수'] * 0.6)
            guro_data['관할면적'] = 20.12
            
            # 금천구 데이터
            geumcheon_data = guro_geumcheon_row.copy()
            geumcheon_data['관할구역명'] = '금천구'
            geumcheon_data['독거노인가구수'] = int(guro_geumcheon_row['독거노인가구수'] * 0.4)
            geumcheon_data['고령인구수'] = int(guro_geumcheon_row['고령인구수'] * 0.4)
            geumcheon_data['유아인구수'] = int(guro_geumcheon_row['유아인구수'] * 0.4)
            geumcheon_data['등록장애인수'] = int(guro_geumcheon_row['등록장애인수'] * 0.4)
            geumcheon_data['1인가구수'] = int(guro_geumcheon_row['1인가구수'] * 0.4)
            geumcheon_data['관할면적'] = 13.02
            
            # 분리된 데이터로 교체
            vulnerable_df = vulnerable_df[vulnerable_df['관할구역명'] != '구로구, 금천구'].copy()
            vulnerable_df = pd.concat([vulnerable_df, pd.DataFrame([guro_data]), pd.DataFrame([geumcheon_data])], ignore_index=True)
        
        # 취약자 밀도 계산
        vulnerable_df['총취약자수'] = (
            vulnerable_df['독거노인가구수'] + 
            vulnerable_df['고령인구수'] + 
            vulnerable_df['유아인구수'] + 
            vulnerable_df['등록장애인수'] + 
            vulnerable_df['1인가구수']
        )
        vulnerable_df['취약자밀도'] = vulnerable_df['총취약자수'] / vulnerable_df['관할면적']
        print(f"✅ 재난안전취약자 데이터: {len(vulnerable_df)}개 구")
        
        # === 2.3 노후주택 데이터 (구별) ===
        print("🏠 노후주택 데이터 처리 중...")
        housing_df = pd.read_csv('dataset/4_select_feature/노후기간별_주택현황_selected_features.csv')
        housing_df = housing_df[housing_df['구명'] != '소계'].copy()
        
        # 면적 데이터 - 소계 값 사용
        gu_area_raw = area_df[area_df['동명'] == '소계'].copy()
        print(f"소계 행 개수: {len(gu_area_raw)}")
        print("소계 데이터 컬럼:", gu_area_raw.columns.tolist())
        
        if len(gu_area_raw) > 0:
            gu_area = gu_area_raw[['구명', '면적_km2']].copy()
            gu_area.columns = ['구명', '총면적_km2']
        else:
            print("⚠️ 소계 데이터가 없어서 동별 면적을 구별로 집계합니다.")
            gu_area = area_df[area_df['동명'] != '소계'].groupby('구명')['면적_km2'].sum().reset_index()
            gu_area.columns = ['구명', '총면적_km2']
        
        # 노후 주택 가중치 계산
        housing_df['weighted_old_housing'] = (
            housing_df['30년이상_주택수'] * 1.5 + 
            housing_df['20년~30년미만_주택수']
        )
        
        # 디버깅 정보 추가
        print("노후주택 데이터 구명 샘플:")
        print(housing_df['구명'].head().tolist())
        print("면적 데이터 구명 샘플:")
        print(gu_area['구명'].head().tolist())
        
        # 데이터 병합 - 구명으로 직접 병합
        housing_merged = pd.merge(housing_df, gu_area, on='구명', how='inner')
        housing_merged['housing_density'] = housing_merged['weighted_old_housing'] / housing_merged['총면적_km2']
        print(f"✅ 노후주택 데이터: {len(housing_merged)}개 구")
        
        # === 2.4 구조출동 데이터 (좌표별) ===
        print("🚒 구조출동 데이터 처리 중...")
        rescue_df = pd.read_csv('dataset/4_select_feature/서울시_구조출동_selected_features.csv')
        
        # 유효한 좌표만 필터링
        valid_coord_mask = (
            (rescue_df['피해지역_경도'].notna()) & 
            (rescue_df['피해지역_위도'].notna()) &
            (rescue_df['피해지역_경도'] != 0) &
            (rescue_df['피해지역_위도'] != 0) &
            (rescue_df['피해지역_경도'] > 126) &
            (rescue_df['피해지역_경도'] < 128) &
            (rescue_df['피해지역_위도'] > 37) &
            (rescue_df['피해지역_위도'] < 38)
        )
        rescue_valid = rescue_df[valid_coord_mask].copy()
        print(f"✅ 유효한 구조출동 좌표: {len(rescue_valid):,}개")
        
        # 구조출동을 동별로 집계 (각 좌표는 값 1)
        rescue_by_gu = rescue_valid['발생지역_시군구명'].value_counts().to_dict()
        print(f"✅ 구조출동 구별 집계: {len(rescue_by_gu)}개 구")
        
        # 3. 동별 기준으로 데이터 통합
        print("\n🔗 동별 기준으로 데이터 통합 중...")
        
        # 기본 동별 데이터프레임 생성
        base_dong_df = dong_boundary[['구명', 'ADM_NM']].copy()
        base_dong_df.columns = ['구명', '동명']
        
        # 3.1 취약연령 데이터 병합 (이미 동별)
        dong_integrated = pd.merge(
            base_dong_df,
            vulnerable_age_data[['구', '동', '취약연령밀도']],
            left_on=['구명', '동명'], 
            right_on=['구', '동'],
            how='left'
        )
        
        # 구명 정리를 위해 동별 데이터에도 clean 컬럼 추가
        dong_integrated['구명_clean'] = dong_integrated['구명'].str.replace('구', '')
        
        # 3.2 재난안전취약자 데이터 병합 (구별 → 동별 확장)
        vulnerable_df['구명_clean'] = vulnerable_df['관할구역명'].str.replace('구', '')
        dong_integrated = pd.merge(
            dong_integrated,
            vulnerable_df[['구명_clean', '취약자밀도']],
            on='구명_clean',
            how='left'
        )
        
        # 3.3 노후주택 데이터 병합 (구별 → 동별 확장) - 구명으로 직접 병합
        dong_integrated = pd.merge(
            dong_integrated,
            housing_merged[['구명', 'housing_density']],
            on='구명',
            how='left'
        )
        
        # 3.4 구조출동 데이터 병합 (구별 → 동별 확장)
        # 구조출동 데이터의 구명 확인 및 매핑 개선
        print("구조출동 데이터 구명 샘플:")
        print(list(rescue_by_gu.keys())[:10])
        
        # 구조출동 구명에서 "서울특별시 " 제거
        rescue_by_gu_clean = {}
        for gu_name, count in rescue_by_gu.items():
            clean_gu_name = gu_name.replace('서울특별시 ', '').replace('서울시 ', '')
            rescue_by_gu_clean[clean_gu_name] = count
        
        dong_integrated['구조출동건수'] = dong_integrated['구명'].map(rescue_by_gu_clean).fillna(0)
        # 구별 동 개수로 나누어 동별 평균 계산
        gu_dong_count = dong_integrated.groupby('구명').size().to_dict()
        dong_integrated['구조출동밀도'] = dong_integrated.apply(
            lambda row: rescue_by_gu_clean.get(row['구명'], 0) / gu_dong_count.get(row['구명'], 1), axis=1
        )
        
        print(f"✅ 통합 데이터: {len(dong_integrated)}개 동")
        
        # 4. 각 데이터 MinMax 정규화 및 가중치 적용
        print("\n⚖️ 데이터 정규화 및 가중치 적용 중...")
        
        scaler = MinMaxScaler()
        
        # 결측값을 0으로 채우기
        dong_integrated = dong_integrated.fillna(0)
        
        # 각 지표별 정규화
        dong_integrated['취약연령_정규화'] = scaler.fit_transform(dong_integrated[['취약연령밀도']]).flatten()
        dong_integrated['취약자_정규화'] = scaler.fit_transform(dong_integrated[['취약자밀도']]).flatten()
        dong_integrated['노후주택_정규화'] = scaler.fit_transform(dong_integrated[['housing_density']]).flatten()
        dong_integrated['구조출동_정규화'] = scaler.fit_transform(dong_integrated[['구조출동밀도']]).flatten()
        
        # 가중치 적용 및 종합 점수 계산
        dong_integrated['취약연령_가중'] = dong_integrated['취약연령_정규화'] * 0.286
        dong_integrated['취약자_가중'] = dong_integrated['취약자_정규화'] * 0.324
        dong_integrated['노후주택_가중'] = dong_integrated['노후주택_정규화'] * 0.466
        dong_integrated['구조출동_가중'] = dong_integrated['구조출동_정규화'] * (-0.07)
        
        # 종합 재난 위험도 점수 계산
        dong_integrated['종합위험도'] = (
            dong_integrated['취약연령_가중'] + 
            dong_integrated['취약자_가중'] + 
            dong_integrated['노후주택_가중'] + 
            dong_integrated['구조출동_가중']
        )
        
        print("정규화 및 가중치 적용 완료!")
        print(f"종합위험도 범위: {dong_integrated['종합위험도'].min():.3f} ~ {dong_integrated['종합위험도'].max():.3f}")
        
        # 5. 동 경계 데이터와 병합
        print("\n🗺️ 지도 데이터 병합 중...")
        dong_final = dong_boundary.merge(
            dong_integrated,
            left_on=['구명', 'ADM_NM'],
            right_on=['구명', '동명'],
            how='left'
        )
        
        # 6. 서울시 중심 좌표 계산
        bounds = dong_boundary.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        print(f"📍 서울시 중심좌표: 위도 {center_lat:.4f}, 경도 {center_lon:.4f}")
        
        # 7. 색상 함수 정의 (종합 위험도용)
        def get_color(value):
            """종합 위험도에 따른 색상 반환 (보라색-빨간색 계열)"""
            if pd.isna(value) or value == 0:
                return '#F0F0F0'  # 연한 회색 (데이터 없음)
            
            # 0-1 범위의 값을 색상으로 변환 (보라색-빨간색 그라데이션)
            if value <= 0.2:
                return '#E6F0FF'  # 매우 연한 파란색
            elif value <= 0.4:
                return '#B19CD9'  # 연한 보라색
            elif value <= 0.6:
                return '#8A2BE2'  # 보라색
            elif value <= 0.8:
                return '#FF4500'  # 주황빨간색
            else:
                return '#8B0000'  # 어두운 빨간색
        
        # 8. Folium 지도 생성
        print("\n🗺️ 종합 재난 위험도 히트맵 생성 중...")
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='CartoDB positron'
        )
        
        # 9. 구 경계 추가 (참조용)
        print("구 경계 추가 (참조용)...")
        folium.GeoJson(
            gu_boundary.to_json(),
            style_function=lambda feature: {
                'fillColor': 'none',
                'color': '#333333',
                'weight': 2.5,
                'opacity': 0.8,
                'fillOpacity': 0
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['구명'], 
                aliases=['구:']
            )
        ).add_to(m)
        
        # 10. 동별 종합 재난 위험도 히트맵 추가
        print("동별 종합 재난 위험도 히트맵 추가...")
        
        for idx, row in dong_final.iterrows():
            risk_score = row.get('종합위험도', 0)
            fill_color = get_color(risk_score)
            
            # 구명, 동명 표시 형식 개선
            if pd.notna(row.get('구명')):
                gu_name = row['구명']
            elif pd.notna(row.get('ADM_CD')):
                gu_code = str(row['ADM_CD'])[:5]
                gu_name = gu_code_mapping.get(gu_code, f'구_{gu_code}')
            else:
                gu_name = 'N/A구'
            
            dong_name = row['ADM_NM'] if pd.notna(row.get('ADM_NM')) else 'N/A동'
            title_text = f"{gu_name}, {dong_name}"
            
            # 동 경계에 색상 적용
            folium.GeoJson(
                row.geometry,
                style_function=lambda x, color=fill_color: {
                    'fillColor': color,
                    'color': '#4A0080',  # 어두운 보라색 테두리
                    'weight': 1,
                    'opacity': 0.7,
                    'fillOpacity': 0.8
                },
                popup=folium.Popup(
                    f"""
                    <div style="font-family: Arial; padding: 10px; width: 320px;">
                    <h4 style="margin: 0; color: #4A0080;">🚨 {title_text}</h4>
                    <hr style="margin: 5px 0;">
                    <p><strong>🔥 종합 위험도:</strong> {risk_score:.3f}</p>
                    <hr style="margin: 5px 0;">
                    <div style="font-size: 12px;">
                    <p><strong>📊 구성 요소 (가중치):</strong></p>
                    <p>👶🧓 취약연령 (28.6%): {row.get('취약연령_가중', 0):.3f}</p>
                    <p>🚨 재난취약자 (32.4%): {row.get('취약자_가중', 0):.3f}</p>
                    <p>🏠 노후주택 (46.6%): {row.get('노후주택_가중', 0):.3f}</p>
                    <p>🚒 구조출동 (-7%): {row.get('구조출동_가중', 0):.3f}</p>
                    </div>
                    <hr style="margin: 5px 0;">
                    <div style="font-size: 11px; color: #666;">
                    <p><strong>원본 값:</strong></p>
                    <p>취약연령밀도: {row.get('취약연령밀도', 0):.1f} 명/km²</p>
                    <p>취약자밀도: {row.get('취약자밀도', 0):.1f} 명/km²</p>
                    <p>노후주택밀도: {row.get('housing_density', 0):.1f} 호/km²</p>
                    <p>구조출동밀도: {row.get('구조출동밀도', 0):.2f} 건/동</p>
                    </div>
                    </div>
                    """,
                    max_width=350
                ),
                tooltip=f"{title_text}: 위험도 {risk_score:.3f}"
            ).add_to(m)
        
        # 11. 범례 추가
        print("범례 추가...")
        legend_html = '''
        <div style="position: fixed; top: 10px; right: 10px; width: 380px; 
                    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,249,250,0.95));
                    border: none; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                    backdrop-filter: blur(10px); padding: 20px; font-family: Arial; z-index: 9999;">
        
        <h3 style="margin: 0 0 15px 0; text-align: center; color: #4A0080; font-size: 18px;">
            🚨 종합 재난 위험도 분석
        </h3>
        
        <div style="margin-bottom: 15px;">
            <p style="margin: 5px 0; font-weight: 600; color: #4A0080;">📊 구성 요소 및 가중치:</p>
            <div style="background: #F8F0FF; padding: 10px; border-radius: 8px; font-size: 11px;">
                <p style="margin: 2px 0;">👶🧓 <strong>취약연령층 밀도</strong>: 28.6%</p>
                <p style="margin: 2px 0;">🚨 <strong>재난안전취약자 밀도</strong>: 32.4%</p>
                <p style="margin: 2px 0;">🏠 <strong>노후주택 밀도</strong>: 46.6%</p>
                <p style="margin: 2px 0;">🚒 <strong>구조출동 밀도</strong>: -0.07%</p>
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <p style="margin: 5px 0; font-weight: 600; color: #4A0080;">🎨 위험도 색상 범례:</p>
            <div style="display: flex; flex-direction: column; gap: 5px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #E6F0FF; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">매우 낮음 (0.0~0.2)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #B19CD9; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">낮음 (0.2~0.4)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #8A2BE2; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">보통 (0.4~0.6)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #FF4500; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">높음 (0.6~0.8)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #8B0000; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">매우 높음 (0.8~1.0)</span>
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <p style="margin: 5px 0; font-weight: 600; color: #4A0080;">🔍 분석 방법:</p>
            <div style="font-size: 11px; color: #666; line-height: 1.4;">
                • 각 지표를 MinMax 정규화 (0~1)<br>
                • 가중치 적용 후 합산<br>
                • 동 단위 세밀한 분석<br>
                • 4개 위험요소 종합 평가
            </div>
        </div>
        
        <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #B19CD9, transparent); margin: 15px 0;">
        
        <div style="text-align: center;">
            <div style="font-size: 11px; color: #4A0080; margin-bottom: 5px;">
                🎯 종합적 재난 위험도 평가
            </div>
            <div style="font-size: 10px; color: #666;">
                색상이 진할수록 재난 위험도가 높음
            </div>
        </div>
        
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 12. 지도 저장
        output_file = 'figure/종합_재난위험도_히트맵.html'
        m.save(output_file)
        
        print(f"\n✅ 종합 재난 위험도 히트맵 생성 완료!")
        print(f"📁 저장 위치: {output_file}")
        
        # 13. 통계 요약 출력
        print(f"\n📊 종합 분석 결과 요약:")
        print(f"전체 동 수: {len(dong_integrated)}개")
        print(f"평균 종합 위험도: {dong_integrated['종합위험도'].mean():.3f}")
        print(f"최대 종합 위험도: {dong_integrated['종합위험도'].max():.3f}")
        print(f"최소 종합 위험도: {dong_integrated['종합위험도'].min():.3f}")
        
        print(f"\n🔝 종합 위험도 상위 15개 동:")
        top_risk = dong_integrated.nlargest(15, '종합위험도')[
            ['구명', '동명', '종합위험도', '취약연령_가중', '취약자_가중', '노후주택_가중', '구조출동_가중']
        ]
        for idx, row in top_risk.iterrows():
            print(f"  {row['구명']} {row['동명']}: {row['종합위험도']:.3f} "
                  f"(취약연령:{row['취약연령_가중']:.3f}, 취약자:{row['취약자_가중']:.3f}, "
                  f"노후주택:{row['노후주택_가중']:.3f}, 구조출동:{row['구조출동_가중']:.3f})")
        
        # 14. 구별 집계 통계
        print(f"\n🏘️ 구별 평균 위험도 상위 10개:")
        gu_risk_stats = dong_integrated.groupby('구명').agg({
            '종합위험도': 'mean',
            '취약연령_가중': 'mean',
            '취약자_가중': 'mean', 
            '노후주택_가중': 'mean',
            '구조출동_가중': 'mean',
            '동명': 'count'
        }).round(3)
        gu_risk_stats.columns = ['평균위험도', '취약연령', '취약자', '노후주택', '구조출동', '동수']
        gu_risk_stats = gu_risk_stats.sort_values('평균위험도', ascending=False)
        
        for idx, (gu, row) in enumerate(gu_risk_stats.head(10).iterrows()):
            print(f"  {idx+1}. {gu}: {row['평균위험도']:.3f} "
                  f"({row['동수']:.0f}개동, 취약연령:{row['취약연령']:.3f}, 취약자:{row['취약자']:.3f}, "
                  f"노후주택:{row['노후주택']:.3f}, 구조출동:{row['구조출동']:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_comprehensive_disaster_risk_heatmap()
    if success:
        print("\n🎉 종합 재난 위험도 히트맵 생성 완료!")
    else:
        print("\n💥 히트맵 생성 실패!") 