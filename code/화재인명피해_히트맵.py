# -*- coding: utf-8 -*-
import geopandas as gpd
import folium
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

def create_fire_casualty_heatmap():
    """
    구별 화재 인명피해 소계 히트맵 생성
    """
    print("🔥 화재 인명피해 히트맵 생성 시작...")
    
    try:
        # 1. 데이터 로드
        print("\n📂 데이터 로딩 중...")
        
        # 구 경계 데이터
        gu_boundary = gpd.read_file('../dataset/서울시_행정구역_경계/서울시_구경계.shp', encoding='cp949')
        gu_boundary = gu_boundary.to_crs('EPSG:4326')
        gu_boundary['구명'] = gu_boundary['SGG_NM'].str.replace('서울특별시 ', '')
        print(f"✅ 구 경계 데이터: {len(gu_boundary)}개 구")
        
        # 동 경계 데이터
        dong_boundary = gpd.read_file('../dataset/서울시_행정구역_경계/서울시_동경계.shp', encoding='cp949')
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
        
        # 화재발생 현황 데이터
        fire_df = pd.read_csv('../dataset/2_filtering/화재발생+현황_20250710140523_구별데이터.csv', encoding='utf-8-sig')
        print(f"✅ 화재발생 현황 데이터: {len(fire_df)}개 구")
        print("화재발생 현황 데이터 컬럼:")
        print(fire_df.columns.tolist())
        print("\n화재발생 현황 데이터 샘플:")
        print(fire_df.head())
        
        # 2. 데이터 전처리
        print("\n🔧 데이터 전처리 중...")
        
        # 구명 정리 (동별(2) 컬럼을 구명으로 사용)
        fire_df['구명'] = fire_df['동별(2)'].str.strip()
        fire_df['인명피해_소계'] = fire_df['2024_인명피해(명)_소계']
        fire_df['화재발생_소계'] = fire_df['2024_발생(건)_소계']
        fire_df['사망자_소계'] = fire_df['2024_사망(명)_소계']
        fire_df['부상자_소계'] = fire_df['2024_부상(명)_소계']
        
        # 숫자형 변환 (빈 문자열이나 '-' 처리)
        fire_df['인명피해_소계'] = pd.to_numeric(fire_df['인명피해_소계'].replace(['-', ''], 0), errors='coerce').fillna(0)
        fire_df['화재발생_소계'] = pd.to_numeric(fire_df['화재발생_소계'].replace(['-', ''], 0), errors='coerce').fillna(0)
        fire_df['사망자_소계'] = pd.to_numeric(fire_df['사망자_소계'].replace(['-', ''], 0), errors='coerce').fillna(0)
        fire_df['부상자_소계'] = pd.to_numeric(fire_df['부상자_소계'].replace(['-', ''], 0), errors='coerce').fillna(0)
        
        print("인명피해 상위 10개 구:")
        print(fire_df.nlargest(10, '인명피해_소계')[['구명', '인명피해_소계', '사망자_소계', '부상자_소계', '화재발생_소계']])
        
        # 3. Min-Max Scaling
        print("\n⚖️ Min-Max Scaling 적용 중...")
        scaler = MinMaxScaler()
        fire_df['casualty_normalized'] = scaler.fit_transform(fire_df[['인명피해_소계']]).flatten()
        
        print(f"정규화 결과:")
        print(f"원본 인명피해 범위: {fire_df['인명피해_소계'].min():.0f} ~ {fire_df['인명피해_소계'].max():.0f}명")
        print(f"정규화 범위: {fire_df['casualty_normalized'].min():.2f} ~ {fire_df['casualty_normalized'].max():.2f}")
        
        # 4. 경계 데이터와 병합
        print("\n🗺️ 지도 데이터 병합 중...")
        
        # 구명이 이미 "종로구", "중구" 형태이므로 직접 매핑
        gu_merged = gu_boundary.merge(fire_df, left_on='구명', right_on='구명', how='left')
        print(f"지도 데이터 병합 결과: {len(gu_merged)}개 구")
        
        # 5. 서울시 중심 좌표 계산
        bounds = gu_boundary.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        print(f"📍 서울시 중심좌표: 위도 {center_lat:.4f}, 경도 {center_lon:.4f}")
        
        # 6. 색상 함수 정의
        def get_color(value):
            """정규화된 값에 따른 색상 반환"""
            if pd.isna(value):
                return '#CCCCCC'  # 회색 (데이터 없음)
            
            # 0-1 범위의 값을 색상으로 변환 (빨간색 계열)
            if value <= 0.2:
                return '#FFF0F0'  # 매우 연한 분홍
            elif value <= 0.4:
                return '#FFB3B3'  # 연한 분홍
            elif value <= 0.6:
                return '#FF6666'  # 분홍
            elif value <= 0.8:
                return '#FF3333'  # 빨간색
            else:
                return '#CC0000'  # 진한 빨간색
        
        # 7. Folium 지도 생성
        print("\n🗺️ 인터랙티브 지도 생성 중...")
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='CartoDB positron'
        )
        
        # 8. 동 경계 추가 (배경)
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
        
        # 9. 구별 화재 인명피해 히트맵 추가
        print("구별 화재 인명피해 히트맵 추가...")
        
        for idx, row in gu_merged.iterrows():
            casualty_normalized = row.get('casualty_normalized', np.nan)
            fill_color = get_color(casualty_normalized)
            
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
                    <div style="font-family: Arial; padding: 15px; width: 280px; background: linear-gradient(135deg, #fff, #f8f9fa); border-radius: 10px;">
                        <h4 style="margin: 0 0 10px 0; color: #DC143C; text-align: center;">🔥 {row.get('구명', 'N/A')}</h4>
                        <hr style="margin: 10px 0; border: none; height: 1px; background: linear-gradient(90deg, transparent, #DC143C, transparent);">
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0;">
                            <div style="background: #FFE5E5; padding: 8px; border-radius: 5px; text-align: center;">
                                <div style="font-size: 18px; font-weight: bold; color: #DC143C;">{row.get('인명피해_소계', 0):.0f}</div>
                                <div style="font-size: 11px; color: #666;">총 인명피해</div>
                            </div>
                            <div style="background: #F0F0F0; padding: 8px; border-radius: 5px; text-align: center;">
                                <div style="font-size: 18px; font-weight: bold; color: #2C3E50;">{row.get('화재발생_소계', 0):.0f}</div>
                                <div style="font-size: 11px; color: #666;">총 화재발생</div>
                            </div>
                        </div>
                        
                        <div style="margin: 10px 0;">
                            <div style="display: flex; justify-content: space-between; margin: 5px 0; padding: 5px; background: #FFF5F5; border-radius: 3px;">
                                <span style="font-size: 12px; color: #666;">사망자:</span>
                                <span style="font-weight: bold; color: #DC143C;">{row.get('사망자_소계', 0):.0f}명</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin: 5px 0; padding: 5px; background: #FFF5F5; border-radius: 3px;">
                                <span style="font-size: 12px; color: #666;">부상자:</span>
                                <span style="font-weight: bold; color: #DC143C;">{row.get('부상자_소계', 0):.0f}명</span>
                            </div>
                        </div>
                        
                        <hr style="margin: 10px 0; border: none; height: 1px; background: #E0E0E0;">
                        
                        <div style="text-align: center;">
                            <div style="font-size: 11px; color: #666; margin: 3px 0;">정규화 점수</div>
                            <div style="font-size: 14px; font-weight: bold; color: #DC143C;">{row.get('casualty_normalized', 0):.3f}</div>
                        </div>
                        
                        <div style="margin-top: 10px; padding: 8px; background: #F8F9FA; border-radius: 5px; text-align: center;">
                            <div style="font-size: 10px; color: #7F8C8D;">
                                💡 2024년 화재발생 인명피해 현황<br>
                                서울시 소방재난본부 공식 통계
                            </div>
                        </div>
                    </div>
                    """,
                    max_width=320
                ),
                tooltip=f"{row.get('구명', 'N/A')}: 인명피해 {row.get('인명피해_소계', 0):.0f}명"
            ).add_to(m)
        
        # 10. 범례 추가
        print("범례 추가...")
        legend_html = '''
        <div style="position: fixed; top: 10px; right: 10px; width: 340px; 
                    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,249,250,0.95));
                    border: none; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                    backdrop-filter: blur(10px); padding: 20px; font-family: Arial; z-index: 9999;">
        
        <h3 style="margin: 0 0 15px 0; text-align: center; color: #DC143C; font-size: 18px;">
            🔥 서울시 구별 화재 인명피해 현황
        </h3>
        
        <div style="margin-bottom: 15px; text-align: center; background: #FFE5E5; padding: 10px; border-radius: 8px;">
            <div style="font-size: 14px; color: #DC143C; font-weight: bold;">2024년 화재발생 인명피해 통계</div>
            <div style="font-size: 11px; color: #666; margin-top: 3px;">서울시 소방재난본부 공식 데이터</div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <p style="margin: 5px 0; font-weight: 600; color: #2C3E50;">🎨 인명피해 수준별 색상:</p>
            <div style="display: flex; flex-direction: column; gap: 5px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 25px; height: 15px; background: #FFF0F0; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">매우 적음 (0.0~0.2)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 25px; height: 15px; background: #FFB3B3; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">적음 (0.2~0.4)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 25px; height: 15px; background: #FF6666; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">보통 (0.4~0.6)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 25px; height: 15px; background: #FF3333; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">많음 (0.6~0.8)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 25px; height: 15px; background: #CC0000; border: 1px solid #ddd; margin-right: 8px; border-radius: 3px;"></div>
                    <span style="font-size: 12px;">매우 많음 (0.8~1.0)</span>
                </div>
            </div>
        </div>
        
        <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #BDC3C7, transparent); margin: 15px 0;">
        
        <div style="margin-bottom: 10px;">
            <div style="font-size: 12px; color: #2C3E50; font-weight: 600; margin-bottom: 5px;">📊 포함 항목:</div>
            <div style="font-size: 11px; color: #666; line-height: 1.4;">
                ▪ 인명피해 소계 (사망 + 부상)<br>
                ▪ 화재발생 건수<br>
                ▪ Min-Max 정규화 적용
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 15px;">
            <div style="font-size: 11px; color: #7F8C8D; margin-bottom: 3px;">
                ⚠️ 색상이 진할수록 인명피해가 많음
            </div>
            <div style="font-size: 10px; color: #95A5A6;">
                클릭하면 상세 정보를 확인할 수 있습니다
            </div>
        </div>
        
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 11. 지도 저장
        import os
        os.makedirs('../figure', exist_ok=True)
        output_file = '../figure/화재인명피해_히트맵.html'
        m.save(output_file)
        
        print(f"\n✅ 화재 인명피해 히트맵 생성 완료!")
        print(f"📁 저장 위치: {output_file}")
        
        # 12. 통계 요약 출력
        print(f"\n📊 분석 결과 요약:")
        print(f"전체 구 수: {len(fire_df)}개")
        print(f"총 인명피해: {fire_df['인명피해_소계'].sum():.0f}명")
        print(f"평균 구별 인명피해: {fire_df['인명피해_소계'].mean():.1f}명")
        print(f"최대 인명피해: {fire_df['인명피해_소계'].max():.0f}명")
        print(f"최소 인명피해: {fire_df['인명피해_소계'].min():.0f}명")
        
        print(f"\n🔝 인명피해 상위 10개 구:")
        top_casualty = fire_df.nlargest(10, '인명피해_소계')[
            ['구명', '인명피해_소계', '사망자_소계', '부상자_소계', '화재발생_소계', 'casualty_normalized']
        ]
        for idx, row in top_casualty.iterrows():
            print(f"  {row['구명']}: {row['인명피해_소계']:.0f}명 "
                  f"(사망: {row['사망자_소계']:.0f}, 부상: {row['부상자_소계']:.0f}, "
                  f"화재: {row['화재발생_소계']:.0f}건, 정규화: {row['casualty_normalized']:.3f})")
        
        print(f"\n🔝 화재발생 상위 5개 구:")
        top_fire = fire_df.nlargest(5, '화재발생_소계')[['구명', '화재발생_소계', '인명피해_소계']]
        for idx, row in top_fire.iterrows():
            casualty_rate = (row['인명피해_소계'] / row['화재발생_소계'] * 100) if row['화재발생_소계'] > 0 else 0
            print(f"  {row['구명']}: {row['화재발생_소계']:.0f}건 "
                  f"(인명피해: {row['인명피해_소계']:.0f}명, 피해율: {casualty_rate:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_fire_casualty_heatmap()
    if success:
        print("\n🎉 화재 인명피해 히트맵 생성 완료!")
    else:
        print("\n💥 히트맵 생성 실패!") 