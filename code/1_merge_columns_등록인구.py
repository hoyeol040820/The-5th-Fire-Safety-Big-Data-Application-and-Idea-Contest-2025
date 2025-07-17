import csv
import os

# 파일 경로 설정
input_file = '../dataset/0_original/서울시_등록인구_2025_1분기.csv'
output_dir = '../dataset/1_merge_column_names'
output_file = os.path.join(output_dir, '서울시_등록인구_2025_1분기.csv')

# 출력 디렉토리가 없으면 생성
os.makedirs(output_dir, exist_ok=True)

# CSV 파일 읽기
with open(input_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    lines = list(reader)

# 헤더 정리
header = lines[0]
new_header = ['구', '동'] + header[1:]  # 구, 동 컬럼 추가

# 데이터 처리
processed_data = []
processed_data.append(new_header)

current_gu = ""  # 현재 구를 추적

for i in range(1, len(lines)):
    row = lines[i]
    dong_name = row[0]
    
    # 구와 동 구분
    if dong_name == "합계":
        # 전체 서울시 데이터
        gu = "서울시"
        dong = "합계"
    elif dong_name.endswith("구"):
        # 구 데이터
        gu = dong_name
        dong = "구계"  # 구 전체 데이터
        current_gu = dong_name  # 현재 구 업데이트
    else:
        # 동 데이터
        gu = current_gu
        dong = dong_name
    
    # 새로운 행 생성
    new_row = [gu, dong] + row[1:]
    processed_data.append(new_row)

# 새로운 CSV 파일 생성
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    
    # 모든 행 쓰기
    for row in processed_data:
        writer.writerow(row)

print(f"구와 동을 구분한 파일이 생성되었습니다: {output_file}")
print(f"원본 데이터 행 수: {len(lines)}")
print(f"처리된 데이터 행 수: {len(processed_data)}")
print(f"새로운 헤더: {new_header}")

# 구별 통계 출력
gu_counts = {}
for i in range(1, len(processed_data)):
    gu = processed_data[i][0]
    if gu in gu_counts:
        gu_counts[gu] += 1
    else:
        gu_counts[gu] = 1

print(f"\n=== 구별 데이터 수 ===")
for gu, count in gu_counts.items():
    print(f"{gu}: {count}행")

print("\n구/동 구분 완료!") 