import csv
import os

# 파일 경로 설정
input_file = '../dataset/1_merge_column_names/서울시_등록인구_2025_1분기.csv'
output_dir = '../dataset/2_filtering'
output_file = os.path.join(output_dir, '서울시_등록인구_2025_1분기_동별.csv')

# 출력 디렉토리가 없으면 생성
os.makedirs(output_dir, exist_ok=True)

# CSV 파일 읽기
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    lines = list(reader)

# 헤더 추출 및 시점 컬럼 제거
header = lines[0]
print(f"원본 헤더: {header}")

# 시점 컬럼 제거 (인덱스 3번)
new_header = [header[i] for i in range(len(header)) if i != 3]
print(f"새로운 헤더: {new_header}")

# 필터링된 데이터 저장
filtered_data = []
filtered_data.append(new_header)  # 새로운 헤더 추가

total_rows = 0
filtered_rows = 0

for i in range(1, len(lines)):
    row = lines[i]
    total_rows += 1
    
    # 구와 동 정보 추출
    gu = row[0]
    dong = row[1]
    
    # 세부 동 데이터만 필터링 (합계, 구계 제외)
    if dong != "합계" and dong != "구계":
        # 시점 컬럼 제거 (인덱스 3번)
        new_row = [row[i] for i in range(len(row)) if i != 3]
        filtered_data.append(new_row)
        filtered_rows += 1

# 새로운 CSV 파일 생성
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    
    # 필터링된 데이터 쓰기
    for row in filtered_data:
        writer.writerow(row)

print(f"세부 동 데이터를 필터링한 파일이 생성되었습니다: {output_file}")
print(f"원본 데이터 행 수: {total_rows}")
print(f"필터링된 데이터 행 수: {filtered_rows}")
print(f"제거된 행 수: {total_rows - filtered_rows}")

# 구별 동 개수 통계
gu_dong_counts = {}
for i in range(1, len(filtered_data)):
    gu = filtered_data[i][0]
    if gu in gu_dong_counts:
        gu_dong_counts[gu] += 1
    else:
        gu_dong_counts[gu] = 1

print(f"\n=== 구별 동 데이터 수 (연령별 포함) ===")
for gu, count in gu_dong_counts.items():
    dong_count = count // 22  # 연령별 22개 카테고리로 나누어 실제 동 개수 계산
    print(f"{gu}: {dong_count}개 동 ({count}행)")

# 샘플 데이터 출력
print(f"\n=== 필터링된 데이터 샘플 ===")
for i in range(1, min(6, len(filtered_data))):
    row = filtered_data[i]
    print(f"{row[0]} > {row[1]} : {row[2]} ({row[3]}명)")

print("\n세부 동 데이터 필터링 완료!") 