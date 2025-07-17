import pandas as pd
import os
from datetime import datetime

# 파일 경로 설정
input_file = '../dataset/1_merge_column_names/서울시_구조출동_2023_한강.csv'
output_dir = '../dataset/2_filtering'
output_file = os.path.join(output_dir, '서울시_구조출동_2023_한강_화재.csv')
report_file = os.path.join(output_dir, '화재데이터_분석보고서.txt')

# 출력 디렉토리가 없으면 생성
os.makedirs(output_dir, exist_ok=True)

# CSV 파일 읽기
print("CSV 파일을 읽고 있습니다...")
df = pd.read_csv(input_file, encoding='utf-8')

print(f"전체 데이터 수: {len(df)}")
print(f"ACDNT_CS_NM 컬럼의 고유값들: {df['ACDNT_CS_NM'].unique()}")

# ACDNT_CS_NM이 "화재"인 데이터만 필터링
fire_data = df[df['ACDNT_CS_NM'] == '화재']

print(f"화재 관련 데이터 수: {len(fire_data)}")

# 필터링된 데이터를 새로운 CSV 파일로 저장
fire_data.to_csv(output_file, index=False, encoding='utf-8')

print(f"화재 관련 데이터가 저장되었습니다: {output_file}")
print(f"저장된 데이터 수: {len(fire_data)}")
print(f"컬럼 수: {len(fire_data.columns)}")

# 간단한 통계 정보 출력
print("\n=== 화재 데이터 간단 통계 ===")
prcs_rslt_stats = fire_data['PRCS_RSLT_SE_NM'].value_counts().head(10)
print(prcs_rslt_stats)

# 보고서 생성
report_content = f"""
============================================
서울시 구조출동 2023 한강 화재 데이터 분석 보고서
============================================

분석 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
분석 대상: 서울시_구조출동_2023_한강.csv

============================================
1. 데이터 개요
============================================

• 원본 데이터 총 건수: {len(df):,}건
• 화재 관련 데이터 건수: {len(fire_data):,}건
• 화재 데이터 비율: {len(fire_data)/len(df)*100:.1f}%
• 총 컬럼 수: {len(fire_data.columns)}개

============================================
2. 사고 유형별 분포
============================================

전체 사고 유형 (ACDNT_CS_NM) 분포:
"""

# 전체 사고 유형 분포 추가
accident_types = df['ACDNT_CS_NM'].value_counts()
for idx, (accident_type, count) in enumerate(accident_types.items(), 1):
    if pd.isna(accident_type):
        accident_type = "미상"
    percentage = count / len(df) * 100
    report_content += f"{idx:2d}. {accident_type}: {count:,}건 ({percentage:.1f}%)\n"

report_content += f"""
============================================
3. 화재 관련 처리 결과 분석
============================================

화재 사고 처리 결과 (PRCS_RSLT_SE_NM) 상위 10개:
"""

# 화재 처리 결과 분포 추가
for idx, (result_type, count) in enumerate(prcs_rslt_stats.items(), 1):
    percentage = count / len(fire_data) * 100
    report_content += f"{idx:2d}. {result_type}: {count:,}건 ({percentage:.1f}%)\n"

# 추가 분석 정보
if '계절' in fire_data.columns or 'SEASN_NM' in fire_data.columns:
    season_col = 'SEASN_NM' if 'SEASN_NM' in fire_data.columns else '계절'
    season_stats = fire_data[season_col].value_counts()
    report_content += f"""
============================================
4. 계절별 화재 발생 분포
============================================

"""
    for idx, (season, count) in enumerate(season_stats.items(), 1):
        percentage = count / len(fire_data) * 100
        report_content += f"{idx}. {season}: {count:,}건 ({percentage:.1f}%)\n"

# 지역별 분석
if 'GRNDS_SGG_NM' in fire_data.columns:
    region_stats = fire_data['GRNDS_SGG_NM'].value_counts().head(10)
    report_content += f"""
============================================
5. 지역별 화재 발생 분포 (상위 10개)
============================================

"""
    for idx, (region, count) in enumerate(region_stats.items(), 1):
        percentage = count / len(fire_data) * 100
        report_content += f"{idx:2d}. {region}: {count:,}건 ({percentage:.1f}%)\n"

report_content += f"""
============================================
6. 파일 정보
============================================

• 원본 파일: {input_file}
• 필터링된 파일: {output_file}
• 보고서 파일: {report_file}

============================================
분석 완료
============================================
"""

# 보고서 파일 저장
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"\n보고서가 저장되었습니다: {report_file}")
print("분석 완료!") 