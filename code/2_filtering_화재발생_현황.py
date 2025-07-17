import pandas as pd
import os

# 파일 경로 설정
input_file = '../dataset/1_merge_column_names/화재발생+현황_20250710140523.csv'
output_dir = '../dataset/2_filtering'
output_file = os.path.join(output_dir, '화재발생+현황_20250710140523_구별데이터.csv')

# 출력 디렉토리가 없으면 생성
os.makedirs(output_dir, exist_ok=True)

# CSV 파일 읽기
print("CSV 파일을 읽고 있습니다...")
df = pd.read_csv(input_file, encoding='utf-8')

print(f"원본 데이터 총 행 수: {len(df)}")
print(f"원본 데이터 컬럼 수: {len(df.columns)}")
print(f"동별(1) 컬럼의 고유값들: {df['동별(1)'].unique()}")
print(f"동별(2) 컬럼의 고유값들: {df['동별(2)'].unique()}")

# 1. 동별(1) 컬럼 제거 (모두 "합계"로 되어있어서 의미없음)
df_no_col1 = df.drop(columns=['동별(1)'])

# 2. 동별(2)가 "소계"인 행 제거 (전체 합계 행 제거)
filtered_df = df_no_col1[df_no_col1['동별(2)'] != '소계']

print(f"\n필터링 결과:")
print(f"원본 데이터: {len(df)}행, {len(df.columns)}컬럼")
print(f"동별(1) 컬럼 제거 후: {len(df_no_col1)}행, {len(df_no_col1.columns)}컬럼")
print(f"소계 행 제거 후: {len(filtered_df)}행, {len(filtered_df.columns)}컬럼")
print(f"제거된 행 수: {len(df) - len(filtered_df)}행")
print(f"제거된 컬럼 수: {len(df.columns) - len(filtered_df.columns)}개")

# 필터링된 데이터를 새로운 CSV 파일로 저장
filtered_df.to_csv(output_file, index=False, encoding='utf-8')

print(f"\n필터링된 데이터가 저장되었습니다: {output_file}")

# 간단한 통계 정보 출력
print(f"\n=== 필터링된 데이터 정보 ===")
print(f"총 구별 데이터 수: {len(filtered_df)}")
print(f"포함된 구들: {', '.join(filtered_df['동별(2)'].unique())}")

# 화재 발생 건수 상위 5개 구 출력
top_fire_areas = filtered_df.nlargest(5, '2024_발생(건)_소계')
print(f"\n=== 화재 발생 건수 상위 5개 구 ===")
for idx, row in top_fire_areas.iterrows():
    print(f"{row['동별(2)']}: {row['2024_발생(건)_소계']:,}건")

print("\n필터링 완료!") 