# -*- coding: utf-8 -*-
import geopandas as gpd
import folium
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

def create_dong_vulnerable_age_heatmap():
    """
    동별 취약연령층(0~14세 + 65세이상) 밀도 히트맵 생성
    """
    print("👶🧓 동별 취약연령층 밀도 히트맵 생성 시작...")
    
    try:
        # 1. 데이터 로드
        print("\n📂 데이터 로딩 중...")
        
        # 구 경계 데이터 (참조용)
        gu_boundary = gpd.read_file('dataset/서울시_행정구역_경계/서울시_구경계.shp', encoding='cp949')
        gu_boundary = gu_boundary.to_crs('EPSG:4326')
        gu_boundary['구명'] = gu_boundary['SGG_NM'].str.replace('서울특별시 ', '')
        print(f"✅ 구 경계 데이터: {len(gu_boundary)}개 구")
        
        # 동 경계 데이터 (메인)
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
        
        # 동별 등록인구 데이터
        population_df = pd.read_csv('dataset/4_select_feature/서울시_등록인구_2025_1분기_동별_최종.csv')
        print(f"✅ 동별 등록인구 데이터: {len(population_df)}개 동")
        print("동별 등록인구 데이터 샘플:")
        print(population_df.head())
        
        # 동별 면적 데이터
        area_df = pd.read_csv('dataset/4_select_feature/서울시_행정구역(동별)_면적.csv')
        area_df = area_df[area_df['동명'] != '소계'].copy()  # 소계 제외
        print(f"✅ 동별 면적 데이터: {len(area_df)}개 동")
        
        # 2. 취약연령층 인구 계산
        print("\n👶🧓 취약연령층 인구 계산 중...")
        population_df['취약연령인구'] = population_df['0~14세'] + population_df['65~']
        
        print("취약연령층 인구 상위 5개:")
        print(population_df.nlargest(5, '취약연령인구')[['구', '동', '취약연령인구', '0~14세', '65~']])
        
        # 3. 데이터 병합 (인구 + 면적)
        print("\n🔗 데이터 병합 중...")
        # 구명과 동명 매칭을 위해 정리
        merged_data = pd.merge(
            population_df, 
            area_df[['구명', '동명', '면적_km2']], 
            left_on=['구', '동'], 
            right_on=['구명', '동명'], 
            how='inner'
        )
        print(f"병합 결과: {len(merged_data)}개 동")
        
        # 4. 취약연령층 밀도 계산
        print("\n📊 취약연령층 밀도 계산 중...")
        merged_data['취약연령밀도'] = merged_data['취약연령인구'] / merged_data['면적_km2']
        
        print("취약연령층 밀도 상위 5개:")
        print(merged_data.nlargest(5, '취약연령밀도')[['구', '동', '취약연령밀도', '취약연령인구', '면적_km2']])
        
        # 5. Min-Max Scaling
        print("\n⚖️ Min-Max Scaling 적용 중...")
        scaler = MinMaxScaler()
        merged_data['밀도_normalized'] = scaler.fit_transform(merged_data[['취약연령밀도']]).flatten()
        
        print(f"정규화 결과:")
        print(f"원본 밀도 범위: {merged_data['취약연령밀도'].min():.2f} ~ {merged_data['취약연령밀도'].max():.2f}")
        print(f"정규화 범위: {merged_data['밀도_normalized'].min():.2f} ~ {merged_data['밀도_normalized'].max():.2f}")
        
        # 6. 동 경계 데이터와 병합
        print("\n🗺️ 지도 데이터 병합 중...")
        
        # 디버깅: 매칭 확인
        print("경계 데이터 샘플:")
        print(dong_boundary[['구명', '동명']].head())
        print("인구 데이터 샘플:")
        print(merged_data[['구', '동']].head())
        
        dong_merged = dong_boundary.merge(
            merged_data, 
            left_on=['구명', '동명'], 
            right_on=['구', '동'], 
            how='left'
        )
        print(f"지도 데이터 병합 결과: {len(dong_merged)}개 동")
        
        # 매칭 성공한 동 개수 확인
        matched_count = dong_merged['취약연령밀도'].notna().sum()
        print(f"데이터 매칭 성공: {matched_count}개 동")
        print(f"데이터 매칭 실패: {len(dong_merged) - matched_count}개 동")
        
        if matched_count < 400:  # 대부분 매칭되지 않았다면
            print("\n❌ 매칭 문제 발견! 샘플 확인:")
            # 매칭 안된 경계 데이터 샘플
            unmatched = dong_merged[dong_merged['취약연령밀도'].isna()]
            print("매칭 안된 경계 데이터 샘플:")
            print(unmatched[['구명', '동명']].head(10))
            
            # 인구 데이터의 고유값들 확인
            print("인구 데이터 구 고유값:")
            print(sorted(merged_data['구'].unique()))
            print("인구 데이터 동 고유값 샘플:")
            print(sorted(merged_data['동'].unique())[:20])
        
        # 7. 서울시 중심 좌표 계산
        bounds = dong_boundary.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        print(f"📍 서울시 중심좌표: 위도 {center_lat:.4f}, 경도 {center_lon:.4f}")
        
        # 8. 색상 함수 정의
        def get_color(value):
            """정규화된 값에 따른 색상 반환 (취약연령층용 파란색-보라색 계열)"""
            if pd.isna(value):
                return '#F0F0F0'  # 연한 회색 (데이터 없음)
            
            # 0-1 범위의 값을 색상으로 변환 (파란색-보라색 계열)
            if value <= 0.2:
                return '#E6F3FF'  # 매우 연한 파란색
            elif value <= 0.4:
                return '#B3D9FF'  # 연한 파란색
            elif value <= 0.6:
                return '#66B3FF'  # 중간 파란색
            elif value <= 0.8:
                return '#3399FF'  # 진한 파란색
            else:
                return '#0066CC'  # 매우 진한 파란색
        
        # 9. Folium 지도 생성
        print("\n🗺️ 인터랙티브 지도 생성 중...")
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='CartoDB positron'
        )
        
        # 10. 구 경계 추가 (참조용 굵은 선)
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
        
        # 11. 동별 취약연령층 밀도 히트맵 추가
        print("동별 취약연령층 밀도 히트맵 추가...")
        
        for idx, row in dong_merged.iterrows():
            density_normalized = row.get('밀도_normalized', np.nan)
            fill_color = get_color(density_normalized)
            
            # 구명, 동명 표시 형식 개선 - N/A 방지
            # 구명 우선순위: 병합된 구명 > 매핑된 구명 > ADM_CD로 역추적
            if pd.notna(row.get('구명')):
                gu_name = row['구명']
            elif pd.notna(row.get('ADM_CD')):
                # ADM_CD에서 구 코드 추출하여 매핑
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
                    'color': '#1E3A8A',  # 어두운 파란색 테두리
                    'weight': 1,
                    'opacity': 0.7,
                    'fillOpacity': 0.8
                },
                popup=folium.Popup(
                    f"""
                    <div style="font-family: Arial; padding: 10px; width: 260px;">
                    <h4 style="margin: 0; color: #1E3A8A;">👶🧓 {title_text}</h4>
                    <hr style="margin: 5px 0;">
                    <p><strong>📊 취약연령 밀도:</strong> {row['취약연령밀도'] if pd.notna(row.get('취약연령밀도')) else 0:.2f} 명/km²</p>
                    <p><strong>📈 정규화 값:</strong> {row['밀도_normalized'] if pd.notna(row.get('밀도_normalized')) else 0:.3f}</p>
                    <p><strong>👥 취약연령 인구:</strong> {row['취약연령인구'] if pd.notna(row.get('취약연령인구')) else 0:,.0f} 명</p>
                    <p><strong>📐 동 면적:</strong> {row['면적_km2'] if pd.notna(row.get('면적_km2')) else 0:.2f} km²</p>
                    <hr style="margin: 5px 0;">
                    <div style="font-size: 11px; color: #666;">
                    <p><strong>연령대별 구성:</strong></p>
                    <p>👶 0~14세: {row['0~14세'] if pd.notna(row.get('0~14세')) else 0:,}명</p>
                    <p>🧓 65세이상: {row['65~'] if pd.notna(row.get('65~')) else 0:,}명</p>
                    </div>
                    </div>
                    """,
                    max_width=300
                ),
                tooltip=f"{title_text}: {row['취약연령밀도'] if pd.notna(row.get('취약연령밀도')) else 0:.0f} 명/km²"
            ).add_to(m)
        
        # 12. 범례 추가
        print("범례 추가...")
        legend_html = '''
        <div style="position: fixed; top: 10px; right: 10px; width: 320px; 
                    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,249,250,0.95));
                    border: none; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                    backdrop-filter: blur(10px); padding: 20px; font-family: Arial; z-index: 9999;">
        
        <h3 style="margin: 0 0 15px 0; text-align: center; color: #1E3A8A; font-size: 18px;">
            👶🧓 동별 취약연령층 밀도 분석
        </h3>
        
        <div style="margin-bottom: 15px;">
            <p style="margin: 5px 0; font-weight: 600; color: #1E3A8A;">📊 밀도 계산 공식:</p>
            <div style="background: #F0F8FF; padding: 10px; border-radius: 8px; font-size: 12px; color: #1E3A8A;">
                (0~14세 인구 + 65세이상 인구) ÷ 동 면적
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <p style="margin: 5px 0; font-weight: 600; color: #1E3A8A;">🎨 색상 범례:</p>
            <div style="display: flex; flex-direction: column; gap: 5px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #E6F3FF; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">매우 낮음 (0.0~0.2)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #B3D9FF; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">낮음 (0.2~0.4)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #66B3FF; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">보통 (0.4~0.6)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #3399FF; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">높음 (0.6~0.8)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 15px; background: #0066CC; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">매우 높음 (0.8~1.0)</span>
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <p style="margin: 5px 0; font-weight: 600; color: #1E3A8A;">👥 취약연령층 구성:</p>
            <div style="font-size: 11px; color: #666; line-height: 1.4;">
                👶 유아/아동 (0~14세) + 🧓 고령자 (65세이상)
            </div>
        </div>
        
        <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #B3D9FF, transparent); margin: 15px 0;">
        
        <div style="text-align: center;">
            <div style="font-size: 11px; color: #1E3A8A; margin-bottom: 5px;">
                🏘️ 동 단위 세밀한 분석
            </div>
            <div style="font-size: 11px; color: #666; margin-bottom: 5px;">
                📊 Min-Max 정규화 적용
            </div>
            <div style="font-size: 10px; color: #999;">
                🔵 색상이 진할수록 취약연령층 밀도가 높음
            </div>
        </div>
        
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 13. 지도 저장
        output_file = 'figure/취약연령_히트맵.html'
        m.save(output_file)
        
        print(f"\n✅ 동별 취약연령층 밀도 히트맵 생성 완료!")
        print(f"📁 저장 위치: {output_file}")
        
        # 14. 통계 요약 출력
        print(f"\n📊 분석 결과 요약:")
        print(f"전체 동 수: {len(merged_data)}개")
        print(f"평균 취약연령 밀도: {merged_data['취약연령밀도'].mean():.2f} 명/km²")
        print(f"최대 취약연령 밀도: {merged_data['취약연령밀도'].max():.2f} 명/km²")
        print(f"최소 취약연령 밀도: {merged_data['취약연령밀도'].min():.2f} 명/km²")
        
        print(f"\n🔝 취약연령층 밀도 상위 10개 동:")
        top_vulnerable = merged_data.nlargest(10, '취약연령밀도')[
            ['구', '동', '취약연령밀도', '취약연령인구', '면적_km2', '0~14세', '65~', '밀도_normalized']
        ]
        for idx, row in top_vulnerable.iterrows():
            print(f"  {row['구']} {row['동']}: {row['취약연령밀도']:.2f} 명/km² "
                  f"(취약연령: {row['취약연령인구']:,.0f}명, 면적: {row['면적_km2']:.2f}km², 정규화: {row['밀도_normalized']:.3f})")
        
        # 15. 연령대별 통계
        print(f"\n👶🧓 연령대별 평균:")
        print(f"👶 0~14세 인구: {merged_data['0~14세'].mean():.0f}명")
        print(f"🧓 65세이상 인구: {merged_data['65~'].mean():.0f}명")
        print(f"👥 총 취약연령 인구: {merged_data['취약연령인구'].mean():.0f}명")
        
        # 16. 구별 집계 통계
        print(f"\n🏘️ 구별 취약연령층 통계:")
        gu_stats = merged_data.groupby('구').agg({
            '취약연령인구': 'sum',
            '취약연령밀도': 'mean',
            '동': 'count'
        }).round(2)
        gu_stats.columns = ['총취약연령인구', '평균밀도', '동수']
        gu_stats = gu_stats.sort_values('평균밀도', ascending=False)
        
        print("구별 평균 취약연령층 밀도 상위 5개:")
        for idx, (gu, row) in enumerate(gu_stats.head().iterrows()):
            print(f"  {idx+1}. {gu}: {row['평균밀도']:.2f} 명/km² "
                  f"(총인구: {row['총취약연령인구']:,.0f}명, {row['동수']:.0f}개동)")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_dong_vulnerable_age_heatmap()
    if success:
        print("\n🎉 동별 취약연령층 밀도 히트맵 생성 완료!")
    else:
        print("\n💥 히트맵 생성 실패!") 