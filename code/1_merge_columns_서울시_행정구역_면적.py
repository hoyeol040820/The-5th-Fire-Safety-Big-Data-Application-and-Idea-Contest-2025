# -*- coding: utf-8 -*-
import pandas as pd
import os

# 파일 경로 설정
input_file = 'dataset/0_original/서울시_행정구역(동별)_면적.csv'
output_file = 'dataset/1_merge_column_names/서울시_행정구역(동별)_면적.csv'

# 출력 디렉토리 생성
os.makedirs('dataset/1_merge_column_names', exist_ok=True)

try:
    # CSV 파일의 첫 몇 줄 확인
    print("📂 파일 헤더 구조 확인 중...")
    with open(input_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 5:  # 처음 5줄만 출력
                print(f"줄 {i+1}: {line.strip()}")
            else:
                break
    
    # 데이터 읽기 (헤더를 3줄로 지정)
    print(f"\n✅ 파일 읽기: {input_file}")
    
    # 헤더 3줄을 읽어서 합치기
    header_lines = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for i in range(3):
            line = f.readline().strip().split(',')
            # 따옴표 제거
            line = [col.strip('"') for col in line]
            header_lines.append(line)
    
    print(f"헤더 1줄: {header_lines[0]}")
    print(f"헤더 2줄: {header_lines[1]}")
    print(f"헤더 3줄: {header_lines[2]}")
    
    # 컬럼명 합치기
    merged_columns = []
    for i in range(len(header_lines[0])):
        col_parts = []
        for j in range(3):
            if i < len(header_lines[j]) and header_lines[j][i]:
                part = header_lines[j][i]
                if part not in ['동별(1)', '동별(2)', '동별(3)', '2023']:
                    col_parts.append(part)
        
        # 컬럼명 생성
        if i == 0:
            merged_columns.append('시도명')
        elif i == 1:
            merged_columns.append('구명')
        elif i == 2:
            merged_columns.append('동명')
        elif i == 3:
            merged_columns.append('면적_km2')
        elif i == 4:
            merged_columns.append('구성비_percent')
        elif i == 5:
            merged_columns.append('행정동_수')
        elif i == 6:
            merged_columns.append('법정동_수')
        else:
            merged_columns.append(f'컬럼_{i+1}')
    
    print(f"\n📊 합쳐진 컬럼명: {merged_columns}")
    
    # 실제 데이터 읽기 (4번째 줄부터)
    df = pd.read_csv(input_file, skiprows=3, header=None, encoding='utf-8')
    df.columns = merged_columns[:len(df.columns)]
    
    print(f"원본 데이터 형태: {df.shape}")
    print(f"컬럼: {list(df.columns)}")
    
    # 샘플 데이터 확인
    print(f"\n📋 샘플 데이터 (상위 5개):")
    print(df.head())
    
    # 데이터 타입 확인 및 정리
    print(f"\n🔧 데이터 정리 중...")
    
    # 따옴표 제거
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip('"').str.strip()
    
    # 숫자 컬럼 변환
    numeric_columns = ['면적_km2', '구성비_percent', '행정동_수', '법정동_수']
    for col in numeric_columns:
        if col in df.columns:
            # '-' 값을 0으로 변환
            df[col] = df[col].replace('-', '0')
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 결과 확인
    print(f"\n📊 정리 후 데이터:")
    print(f"데이터 형태: {df.shape}")
    print(f"데이터 타입:")
    print(df.dtypes)
    
    # 통계 요약
    print(f"\n📈 숫자 컬럼 통계:")
    print(df[numeric_columns].describe())
    
    # 구별 통계
    print(f"\n🏙️ 구별 통계:")
    gu_stats = df.groupby('구명').agg({
        '면적_km2': 'sum',
        '행정동_수': 'sum',
        '법정동_수': 'sum'
    }).round(2)
    print(gu_stats.head(10))
    
    # 결측값 확인
    print(f"\n🔍 결측값 확인:")
    print(df.isnull().sum())
    
    # CSV 파일로 저장
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ 파일 저장 완료: {output_file}")
    
    # 보고서 생성
    report_file = 'dataset/1_merge_column_names/서울시_행정구역_면적_처리_보고서.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("서울시 행정구역(동별) 면적 데이터 컬럼 병합 보고서\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"처리 일시: {pd.Timestamp.now()}\n")
        f.write(f"입력 파일: {input_file}\n")
        f.write(f"출력 파일: {output_file}\n\n")
        f.write("처리 내용:\n")
        f.write("1. 3줄로 나뉜 헤더를 하나로 합치기\n")
        f.write("2. 컬럼명 정리 및 한글화\n")
        f.write("3. 데이터 타입 정리\n")
        f.write("4. 결측값 처리\n\n")
        f.write("컬럼 매핑:\n")
        f.write("- 시도명: 첫 번째 컬럼\n")
        f.write("- 구명: 두 번째 컬럼\n")
        f.write("- 동명: 세 번째 컬럼\n")
        f.write("- 면적_km2: 면적 (k㎡)\n")
        f.write("- 구성비_percent: 구성비 (%)\n")
        f.write("- 행정동_수: 행정동 수\n")
        f.write("- 법정동_수: 법정동 수\n\n")
        f.write(f"처리 결과: {df.shape[0]}개 행정동, {df.shape[1]}개 컬럼\n\n")
        f.write("결측값 정보:\n")
        f.write(df.isnull().sum().to_string())
        f.write("\n\n구별 면적 통계 (상위 10개):\n")
        f.write(gu_stats.head(10).to_string())
    
    print(f"\n📄 보고서 생성 완료: {report_file}")
    
except Exception as e:
    print(f"❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc() 