import csv
import os
from datetime import datetime

# 입력 파일 경로
input_file = '../dataset/2_filtering/서울시_등록인구_2025_1분기_동별.csv'
output_file = '../dataset/3_pivot/서울시_등록인구_2025_1분기_동별.csv'
report_file = '../dataset/3_pivot/서울시_등록인구_전처리_보고서.txt'

def preprocess_population_data():
    """
    서울시 등록인구 데이터를 피벗하여 각 구/동별로 한 행으로 만들고,
    연령대별로 컬럼을 분리하는 함수
    """
    print(f"입력 파일: {input_file}")
    print(f"출력 파일: {output_file}")
    print(f"보고서 파일: {report_file}")
    
    # 연령대 정의 (합계는 제외)
    age_groups = [
        '0~4세', '5~9세', '10~14세', '15~19세', '20~24세', '25~29세',
        '30~34세', '35~39세', '40~44세', '45~49세', '50~54세', '55~59세',
        '60~64세', '65~69세', '70~74세', '75~79세', '80~84세', '85~89세',
        '90~94세', '95~99세', '100세 이상'
    ]
    
    # 구/동별 데이터 저장
    districts_data = {}
    
    # 통계 변수
    total_rows_processed = 0
    total_districts = set()
    korean_population = 0
    foreign_population = 0
    total_population = 0
    age_statistics = {}
    
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            total_rows_processed += 1
            district = row['구']
            dong = row['동']
            age_group = row['연령별']
            total_count = int(row['계']) if row['계'] and row['계'] != '-' else 0
            korean_count = int(row['한국인']) if row['한국인'] and row['한국인'] != '-' else 0
            foreign_count = int(row['등록외국인']) if row['등록외국인'] and row['등록외국인'] != '-' else 0
            
            # 통계 수집
            total_districts.add(f"{district}_{dong}")
            
            # 합계는 제외하고 통계만 수집
            if age_group == '합계':
                continue
            
            # 연령대별 통계 수집
            if age_group not in age_statistics:
                age_statistics[age_group] = {'total': 0, 'korean': 0, 'foreign': 0}
            
            age_statistics[age_group]['total'] += total_count
            age_statistics[age_group]['korean'] += korean_count
            age_statistics[age_group]['foreign'] += foreign_count
            
            total_population += total_count
            korean_population += korean_count
            foreign_population += foreign_count
                
            # 구/동 키 생성
            key = f"{district}_{dong}"
            
            # 처음 보는 구/동이면 초기화
            if key not in districts_data:
                districts_data[key] = {
                    '구': district,
                    '동': dong
                }
                # 모든 연령대를 0으로 초기화
                for age in age_groups:
                    districts_data[key][age] = '0'
            
            # 해당 연령대에 값 저장 (계 컬럼 사용)
            if age_group in age_groups:
                districts_data[key][age_group] = str(total_count)
    
    # 결과 파일 작성
    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        # 헤더 작성
        header = ['구', '동'] + age_groups
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        
        # 데이터 작성 (구/동별로 정렬)
        for key in sorted(districts_data.keys()):
            writer.writerow(districts_data[key])
    
    # 보고서 생성
    generate_report(total_rows_processed, len(districts_data), age_groups, 
                   korean_population, foreign_population, total_population, 
                   age_statistics)
    
    print(f"처리 완료!")
    print(f"총 {len(districts_data)}개 구/동 데이터 처리됨")
    print(f"컬럼 구조: 구, 동, {', '.join(age_groups)}")

def generate_report(total_rows, districts_count, age_groups, korean_pop, foreign_pop, total_pop, age_stats):
    """
    전처리 과정에 대한 상세 보고서 생성
    """
    with open(report_file, 'w', encoding='utf-8') as file:
        file.write("="*80 + "\n")
        file.write("서울시 등록인구 데이터 전처리 보고서\n")
        file.write("="*80 + "\n")
        file.write(f"작성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 1. 전처리 작업 개요
        file.write("1. 전처리 작업 개요\n")
        file.write("-"*50 + "\n")
        file.write("• 원본 데이터 형태: 각 구/동별로 연령대마다 별도의 행으로 구성\n")
        file.write("• 변환 후 형태: 각 구/동별로 한 행, 연령대별로 컬럼 분리\n")
        file.write("• 사용된 데이터: '계' 컬럼 (한국인 + 등록외국인 합계)\n")
        file.write("• 제외된 데이터: '합계' 연령대 (중복 데이터 방지)\n\n")
        
        # 2. 데이터 통계
        file.write("2. 데이터 통계\n")
        file.write("-"*50 + "\n")
        file.write(f"• 원본 데이터 행 수: {total_rows:,}개\n")
        file.write(f"• 처리된 구/동 수: {districts_count:,}개\n")
        file.write(f"• 연령대 컬럼 수: {len(age_groups)}개\n")
        file.write(f"• 최종 출력 행 수: {districts_count:,}개 (헤더 제외)\n\n")
        
        # 3. 인구 통계 (합계 제외한 실제 데이터)
        file.write("3. 인구 통계 분석\n")
        file.write("-"*50 + "\n")
        file.write(f"• 총 인구: {total_pop:,}명\n")
        file.write(f"• 한국인: {korean_pop:,}명 ({korean_pop/total_pop*100:.1f}%)\n")
        file.write(f"• 등록외국인: {foreign_pop:,}명 ({foreign_pop/total_pop*100:.1f}%)\n\n")
        
        # 4. 연령대별 통계
        file.write("4. 연령대별 인구 분포\n")
        file.write("-"*50 + "\n")
        file.write(f"{'연령대':<10} {'총 인구':<12} {'한국인':<12} {'등록외국인':<12} {'비율(%)':<8}\n")
        file.write("-"*60 + "\n")
        
        for age in age_groups:
            if age in age_stats:
                total = age_stats[age]['total']
                korean = age_stats[age]['korean']
                foreign = age_stats[age]['foreign']
                ratio = (total / total_pop * 100) if total_pop > 0 else 0
                file.write(f"{age:<10} {total:<12,} {korean:<12,} {foreign:<12,} {ratio:<8.1f}\n")
        
        file.write("\n")
        
        # 5. 처리 과정 상세
        file.write("5. 처리 과정 상세\n")
        file.write("-"*50 + "\n")
        file.write("Step 1: 원본 CSV 파일 읽기\n")
        file.write("  - 컬럼: 구, 동, 연령별, 계, 한국인, 등록외국인\n")
        file.write("  - 인코딩: UTF-8\n\n")
        
        file.write("Step 2: 데이터 피벗 (Pivot) 수행\n")
        file.write("  - 각 구/동별로 데이터 그룹화\n")
        file.write("  - 연령대별 행을 컬럼으로 변환\n")
        file.write("  - '합계' 연령대 제외 (중복 방지)\n\n")
        
        file.write("Step 3: 데이터 값 처리\n")
        file.write("  - 사용 컬럼: '계' (한국인 + 등록외국인 합계)\n")
        file.write("  - 결측값 처리: '-' → 0으로 변환\n")
        file.write("  - 데이터 타입: 문자열로 출력\n\n")
        
        file.write("Step 4: 결과 파일 생성\n")
        file.write("  - 헤더: 구, 동, 21개 연령대 컬럼\n")
        file.write("  - 정렬: 구/동명 기준 오름차순\n")
        file.write("  - 인코딩: UTF-8\n\n")
        
        # 6. 출력 파일 정보
        file.write("6. 출력 파일 정보\n")
        file.write("-"*50 + "\n")
        file.write(f"• 파일명: {os.path.basename(output_file)}\n")
        file.write(f"• 경로: {output_file}\n")
        file.write(f"• 컬럼 구조:\n")
        file.write("  - 구: 서울시 자치구명\n")
        file.write("  - 동: 행정동명\n")
        for i, age in enumerate(age_groups, 3):
            file.write(f"  - {age}: 해당 연령대 총 인구수\n")
        
        file.write("\n")
        file.write("="*80 + "\n")
        file.write("보고서 생성 완료\n")
        file.write("="*80 + "\n")

if __name__ == "__main__":
    preprocess_population_data() 