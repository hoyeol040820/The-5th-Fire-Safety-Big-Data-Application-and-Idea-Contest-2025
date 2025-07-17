# -*- coding: utf-8 -*-
import pandas as pd
import os

# 파일 경로 설정
input_file = 'dataset/3_pivot/서울시_등록인구_2025_1분기_동별.csv'
output_file = 'dataset/4_final/서울시_등록인구_2025_1분기_동별_최종.csv'

# 출력 디렉토리 생성
os.makedirs('dataset/4_final', exist_ok=True)

try:
    # CSV 파일 읽기
    df = pd.read_csv(input_file, encoding='utf-8')
    print(f"✅ 파일 읽기 완료: {input_file}")
    print(f"원본 데이터 형태: {df.shape}")
    print(f"컬럼: {list(df.columns)}")
    
    # 연령대별 그룹화
    result_df = pd.DataFrame()
    
    # 기본 컬럼 복사 (구, 동)
    result_df['구'] = df['구']
    result_df['동'] = df['동']
    
    # 0~14세 = 0~4세 + 5~9세 + 10~14세
    result_df['0~14세'] = df['0~4세'] + df['5~9세'] + df['10~14세']
    
    # 65~ = 65~69세 + 70~74세 + 75~79세 + 80~84세 + 85~89세 + 90~94세 + 95~99세 + 100세 이상
    result_df['65~'] = (df['65~69세'] + df['70~74세'] + df['75~79세'] + 
                       df['80~84세'] + df['85~89세'] + df['90~94세'] + 
                       df['95~99세'] + df['100세 이상'])
    
    # 결과 확인
    print(f"\n📊 변환 결과:")
    print(f"최종 데이터 형태: {result_df.shape}")
    print(f"최종 컬럼: {list(result_df.columns)}")
    
    # 샘플 데이터 출력
    print(f"\n📋 샘플 데이터 (상위 5개):")
    print(result_df.head())
    
    # 통계 요약
    print(f"\n📈 통계 요약:")
    print(result_df.describe())
    
    # CSV 파일로 저장
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ 파일 저장 완료: {output_file}")
    
    # 구별 통계 (참고용)
    print(f"\n🏙️ 구별 통계:")
    gu_stats = result_df.groupby('구')[['0~14세', '65~']].sum().sort_values('0~14세', ascending=False)
    print(gu_stats)
    
    # 보고서 생성
    report_file = 'dataset/4_final/서울시_등록인구_최종_보고서.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("서울시 등록인구 2025년 1분기 동별 데이터 최종 처리 보고서\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"처리 일시: {pd.Timestamp.now()}\n")
        f.write(f"입력 파일: {input_file}\n")
        f.write(f"출력 파일: {output_file}\n\n")
        f.write("처리 내용:\n")
        f.write("1. 0~14세 = 0~4세 + 5~9세 + 10~14세\n")
        f.write("2. 65~ = 65~69세부터 100세 이상까지 합계\n")
        f.write("3. 15~64세 구간은 제외\n\n")
        f.write(f"원본 데이터: {df.shape[0]}개 행정동, {df.shape[1]}개 컬럼\n")
        f.write(f"최종 데이터: {result_df.shape[0]}개 행정동, {result_df.shape[1]}개 컬럼\n\n")
        f.write("구별 통계:\n")
        f.write(gu_stats.to_string())
    
    print(f"\n📄 보고서 생성 완료: {report_file}")
    
except Exception as e:
    print(f"❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc() 