# -*- coding: utf-8 -*-
import pandas as pd
import os

# 파일 경로 설정
input_file = 'dataset/1_merge_column_names/서울시_행정구역(동별)_면적.csv'
output_file = 'dataset/2_filtering/서울시_행정구역(동별)_면적.csv'

# 출력 디렉토리 생성
os.makedirs('dataset/2_filtering', exist_ok=True)

try:
    # CSV 파일 읽기
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    print(f"✅ 파일 읽기 완료: {input_file}")
    print(f"원본 데이터 형태: {df.shape}")
    print(f"원본 컬럼: {list(df.columns)}")
    
    # 필터링: 행정동_수, 법정동_수 컬럼 제거
    columns_to_remove = ['행정동_수', '법정동_수']
    filtered_columns = [col for col in df.columns if col not in columns_to_remove]
    
    print(f"\n🔧 필터링 작업:")
    print(f"제거할 컬럼: {columns_to_remove}")
    print(f"유지할 컬럼: {filtered_columns}")
    
    # 필터링된 데이터프레임 생성
    df_filtered = df[filtered_columns].copy()
    
    print(f"\n📊 필터링 후 결과:")
    print(f"필터링 후 데이터 형태: {df_filtered.shape}")
    print(f"필터링 후 컬럼: {list(df_filtered.columns)}")
    
    # 샘플 데이터 확인
    print(f"\n📋 샘플 데이터 (상위 10개):")
    print(df_filtered.head(10))
    
    # 데이터 타입 확인
    print(f"\n🔍 데이터 타입:")
    print(df_filtered.dtypes)
    
    # 통계 요약
    print(f"\n📈 숫자 컬럼 통계:")
    numeric_cols = ['면적_km2', '구성비_percent']
    if all(col in df_filtered.columns for col in numeric_cols):
        print(df_filtered[numeric_cols].describe())
    
    # 구별 통계
    print(f"\n🏙️ 구별 면적 통계 (상위 10개):")
    if '구명' in df_filtered.columns and '면적_km2' in df_filtered.columns:
        # 소계 행만 필터링하여 구별 통계 생성
        gu_total = df_filtered[df_filtered['동명'] == '소계'].copy()
        gu_stats = gu_total.groupby('구명')['면적_km2'].sum().sort_values(ascending=False)
        print(gu_stats.head(10))
    
    # 동별 면적 상위 10개 (소계 제외)
    print(f"\n📍 동별 면적 상위 10개 (소계 제외):")
    dong_stats = df_filtered[df_filtered['동명'] != '소계'].nlargest(10, '면적_km2')
    print(dong_stats[['구명', '동명', '면적_km2', '구성비_percent']])
    
    # 결측값 확인
    print(f"\n🔍 결측값 확인:")
    print(df_filtered.isnull().sum())
    
    # CSV 파일로 저장
    df_filtered.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ 파일 저장 완료: {output_file}")
    
    # 보고서 생성
    report_file = 'dataset/2_filtering/서울시_행정구역_면적_필터링_보고서.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("서울시 행정구역(동별) 면적 데이터 필터링 보고서\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"처리 일시: {pd.Timestamp.now()}\n")
        f.write(f"입력 파일: {input_file}\n")
        f.write(f"출력 파일: {output_file}\n\n")
        f.write("처리 내용:\n")
        f.write("- 행정동_수 컬럼 제거\n")
        f.write("- 법정동_수 컬럼 제거\n\n")
        f.write("최종 컬럼:\n")
        for i, col in enumerate(df_filtered.columns, 1):
            f.write(f"{i}. {col}\n")
        f.write(f"\n원본 데이터: {df.shape[0]}개 행, {df.shape[1]}개 컬럼\n")
        f.write(f"필터링 후: {df_filtered.shape[0]}개 행, {df_filtered.shape[1]}개 컬럼\n\n")
        f.write("결측값 정보:\n")
        f.write(df_filtered.isnull().sum().to_string())
        f.write("\n\n구별 면적 통계:\n")
        if '구명' in df_filtered.columns and '면적_km2' in df_filtered.columns:
            gu_total = df_filtered[df_filtered['동명'] == '소계'].copy()
            gu_stats = gu_total.groupby('구명')['면적_km2'].sum().sort_values(ascending=False)
            f.write(gu_stats.to_string())
        f.write("\n\n동별 면적 상위 10개 (소계 제외):\n")
        dong_stats = df_filtered[df_filtered['동명'] != '소계'].nlargest(10, '면적_km2')
        f.write(dong_stats[['구명', '동명', '면적_km2', '구성비_percent']].to_string())
    
    print(f"\n📄 보고서 생성 완료: {report_file}")
    
except Exception as e:
    print(f"❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc() 