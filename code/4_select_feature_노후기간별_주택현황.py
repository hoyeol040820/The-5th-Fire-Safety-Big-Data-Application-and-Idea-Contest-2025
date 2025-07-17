# -*- coding: utf-8 -*-
import pandas as pd
import os

# 파일 경로 설정
input_file = 'dataset/3_pivot/노후기간별+주택현황_20250710173050.csv'
output_file = 'dataset/4_select_feature/노후기간별_주택현황_selected_features.csv'

# 출력 디렉토리 생성
os.makedirs('dataset/4_select_feature', exist_ok=True)

try:
    # CSV 파일 읽기
    df = pd.read_csv(input_file, encoding='utf-8')
    print(f"✅ 파일 읽기 완료: {input_file}")
    print(f"원본 데이터 형태: {df.shape}")
    print(f"원본 컬럼: {list(df.columns)}")
    
    # 필요한 컬럼만 선택
    selected_columns = [
        '자치구(1)',              # 시/도 정보
        '자치구(2)',              # 구 정보
        '2023_20년~30년미만_계',   # 20년~30년미만 주택 총계
        '2023_30년이상_계'        # 30년이상 주택 총계
    ]
    
    print(f"\n📊 Feature Selection:")
    print(f"선택할 컬럼: {selected_columns}")
    
    # 컬럼 존재 확인
    missing_columns = [col for col in selected_columns if col not in df.columns]
    if missing_columns:
        print(f"⚠️ 누락된 컬럼: {missing_columns}")
        # 존재하는 컬럼만 선택
        selected_columns = [col for col in selected_columns if col in df.columns]
    
    # 선택된 컬럼으로 필터링
    result_df = df[selected_columns].copy()
    
    # 컬럼명을 더 명확하게 변경
    column_mapping = {
        '자치구(1)': '시도명',
        '자치구(2)': '구명',
        '2023_20년~30년미만_계': '20년~30년미만_주택수',
        '2023_30년이상_계': '30년이상_주택수'
    }
    
    result_df.columns = [column_mapping.get(col, col) for col in result_df.columns]
    
    # 결과 확인
    print(f"\n📊 최종 결과:")
    print(f"최종 데이터 형태: {result_df.shape}")
    print(f"최종 컬럼: {list(result_df.columns)}")
    
    # 샘플 데이터 출력
    print(f"\n📋 샘플 데이터:")
    print(result_df.head(10))
    
    # 통계 요약
    print(f"\n📈 통계 요약:")
    print(result_df.describe())
    
    # 시도명별 정보 확인
    print(f"\n🏙️ 시도명별 정보:")
    print(result_df['시도명'].value_counts())
    
    # 구별 노후주택 현황 (상위 10개)
    print(f"\n🏘️ 구별 노후주택 현황 (20년~30년미만 상위 10개):")
    aging_20_30 = result_df[result_df['구명'] != '소계'].nlargest(10, '20년~30년미만_주택수')
    print(aging_20_30[['구명', '20년~30년미만_주택수', '30년이상_주택수']])
    
    print(f"\n🏚️ 구별 노후주택 현황 (30년이상 상위 10개):")
    aging_30_plus = result_df[result_df['구명'] != '소계'].nlargest(10, '30년이상_주택수')
    print(aging_30_plus[['구명', '20년~30년미만_주택수', '30년이상_주택수']])
    
    # 결측값 확인
    print(f"\n🔍 결측값 확인:")
    print(result_df.isnull().sum())
    
    # 전체 노후주택 비율 계산
    result_df['총_노후주택수'] = result_df['20년~30년미만_주택수'] + result_df['30년이상_주택수']
    result_df['30년이상_비율'] = (result_df['30년이상_주택수'] / result_df['총_노후주택수'] * 100).round(2)
    
    # 노후주택 비율 분석
    print(f"\n📊 노후주택 비율 분석 (30년이상 비율 상위 10개):")
    aging_ratio = result_df[result_df['구명'] != '소계'].nlargest(10, '30년이상_비율')
    print(aging_ratio[['구명', '30년이상_주택수', '총_노후주택수', '30년이상_비율']])
    
    # CSV 파일로 저장 (비율 컬럼 제외하고 원본 형태로)
    result_df_final = result_df[['시도명', '구명', '20년~30년미만_주택수', '30년이상_주택수']].copy()
    result_df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ 파일 저장 완료: {output_file}")
    
    # 보고서 생성
    report_file = 'dataset/4_select_feature/노후기간별_주택현황_처리_보고서.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("노후기간별 주택현황 Feature Selection 보고서\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"처리 일시: {pd.Timestamp.now()}\n")
        f.write(f"입력 파일: {input_file}\n")
        f.write(f"출력 파일: {output_file}\n\n")
        f.write("선택된 Features:\n")
        f.write("1. 시도명 (자치구(1))\n")
        f.write("2. 구명 (자치구(2))\n")
        f.write("3. 20년~30년미만_주택수 (2023_20년~30년미만_계)\n")
        f.write("4. 30년이상_주택수 (2023_30년이상_계)\n\n")
        f.write(f"원본 데이터: {df.shape[0]}개 지역, {df.shape[1]}개 컬럼\n")
        f.write(f"최종 데이터: {result_df_final.shape[0]}개 지역, {result_df_final.shape[1]}개 컬럼\n\n")
        f.write("결측값 정보:\n")
        f.write(result_df_final.isnull().sum().to_string())
        f.write("\n\n통계 요약:\n")
        f.write(result_df_final.describe().to_string())
        f.write("\n\n20년~30년미만 주택수 상위 10개 지역:\n")
        f.write(aging_20_30[['구명', '20년~30년미만_주택수', '30년이상_주택수']].to_string())
        f.write("\n\n30년이상 주택수 상위 10개 지역:\n")
        f.write(aging_30_plus[['구명', '20년~30년미만_주택수', '30년이상_주택수']].to_string())
        f.write("\n\n30년이상 비율 상위 10개 지역:\n")
        f.write(aging_ratio[['구명', '30년이상_주택수', '총_노후주택수', '30년이상_비율']].to_string())
    
    print(f"\n📄 보고서 생성 완료: {report_file}")
    
except Exception as e:
    print(f"❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc() 