import pandas as pd
import os
import csv

# 파일 경로 설정
input_file = '../dataset/0_original/화재발생+현황_20250710140523.csv'
output_dir = '../dataset/1_merge_column_names'
output_file = os.path.join(output_dir, '화재발생+현황_20250710140523.csv')

# 출력 디렉토리가 없으면 생성
os.makedirs(output_dir, exist_ok=True)

# CSV 파일 읽기 (첫 3줄은 헤더로 사용)
with open(input_file, 'r', encoding='utf-8-sig') as f:  # BOM 문제 해결
    reader = csv.reader(f)
    lines = list(reader)

# 첫 3줄을 파싱하여 컬럼명 생성
header_line1 = lines[0]
header_line2 = lines[1]
header_line3 = lines[2]

# 새로운 컬럼명 생성
new_columns = []
for i in range(len(header_line1)):
    if i < 2:  # 첫 두 컬럼은 그대로 사용
        new_columns.append(header_line1[i])
    else:
        # 3줄을 합쳐서 새로운 컬럼명 생성
        year = header_line1[i]
        category = header_line2[i]
        detail = header_line3[i]
        
        # 공백 제거 및 특수문자 정리
        category = category.replace(' ', '')
        detail = detail.replace(' ', '')
        
        # 빈 값이나 중복 제거
        if category == detail:
            new_column_name = f"{year}_{category}"
        else:
            new_column_name = f"{year}_{category}_{detail}"
        
        new_columns.append(new_column_name)

# 데이터 부분 (4번째 줄부터)
data_lines = lines[3:]

# 새로운 CSV 파일 생성
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    
    # 헤더 쓰기
    writer.writerow(new_columns)
    
    # 데이터 쓰기
    for line in data_lines:
        writer.writerow(line)

print(f"컬럼명을 합쳐서 새로운 파일이 생성되었습니다: {output_file}")
print(f"새로운 컬럼명: {new_columns}") 