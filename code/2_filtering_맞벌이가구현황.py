import csv
import os

# 파일 경로 설정
input_file = '../dataset/1_merge_column_names/맞벌이+가구+현황_20250716125811.csv'
output_dir = '../dataset/2_filtering'
output_file = os.path.join(output_dir, '맞벌이+가구+현황_20250716125811.csv')

# 출력 디렉토리가 없으면 생성
os.makedirs(output_dir, exist_ok=True)

# CSV 파일 읽기 및 정리
with open(input_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    lines = list(reader)

# 헤더 정리 (첫 번째 컬럼의 BOM과 따옴표 제거)
if lines:
    # 첫 번째 컬럼의 BOM과 따옴표 제거
    first_column = lines[0][0]
    # BOM 제거
    first_column = first_column.lstrip('\ufeff')
    # 따옴표 제거
    first_column = first_column.strip('"')
    lines[0][0] = first_column

# 정리된 CSV 파일 생성
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    
    # 모든 행 쓰기
    for line in lines:
        writer.writerow(line)

print(f"따옴표를 제거한 파일이 생성되었습니다: {output_file}")
print(f"총 행 수: {len(lines)}")
print(f"헤더: {lines[0]}")
print("따옴표 제거 완료!") 