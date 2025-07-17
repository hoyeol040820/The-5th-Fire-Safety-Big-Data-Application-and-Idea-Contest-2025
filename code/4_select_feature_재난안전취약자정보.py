# -*- coding: utf-8 -*-
import pandas as pd
import os

# 파일 경로 설정
input_file = 'dataset/3_pivot/재난안전취약자정보_0000_서울시소방서별.csv'
output_file = 'dataset/4_select_feature/재난안전취약자정보_selected_features.csv'

# 출력 디렉토리 생성
os.makedirs('dataset/4_select_feature', exist_ok=True)

try:
    # CSV 파일 읽기
    df = pd.read_csv(input_file, encoding='utf-8')
    print(f"✅ 파일 읽기 완료: {input_file}")
    print(f"원본 데이터 형태: {df.shape}")
    print(f"원본 컬럼: {list(df.columns)}")
    
    # 필요한 컬럼만 선택
    selected_columns = [
        'CMPTNC_ZONE_NM',      # 관할구역명 (구 정보)
        'EDRLVNALN_HSHD_CNT',  # 독거노인가구수
        'ADVAG_PPLTN_CNT',     # 고령인구수
        'INFNT_PPLTN_CNT',     # 유아인구수
        'REG_PWDBS_CNT',       # 등록장애인수
        'ONPSHH_CNT',          # 1인가구
        'FIRE_OCRN_NOCS',      # 화재발생건수
        'CMPTNC_AREA'          # 관할면적
    ]
    
    # 컬럼 존재 확인
    missing_columns = [col for col in selected_columns if col not in df.columns]
    if missing_columns:
        print(f"⚠️ 누락된 컬럼: {missing_columns}")
    
    # 선택된 컬럼으로 필터링
    result_df = df[selected_columns].copy()
    
    # 컬럼명을 더 명확하게 변경
    result_df.columns = [
        '관할구역명',
        '독거노인가구수',
        '고령인구수',
        '유아인구수',
        '등록장애인수',
        '1인가구수',
        '화재발생건수',
        '관할면적'
    ]
    
    # 결과 확인
    print(f"\n📊 필터링 결과:")
    print(f"선택된 데이터 형태: {result_df.shape}")
    print(f"선택된 컬럼: {list(result_df.columns)}")
    
    # 샘플 데이터 출력
    print(f"\n📋 샘플 데이터 (상위 10개):")
    print(result_df.head(10))
    
    # 통계 요약
    print(f"\n📈 통계 요약:")
    print(result_df.describe())
    
    # 관할구역별 정보 확인
    print(f"\n🏙️ 관할구역별 정보:")
    print(result_df['관할구역명'].value_counts())
    
    # 구로구, 금천구가 합쳐져 있는 경우 확인
    print(f"\n🔍 특이사항:")
    for idx, row in result_df.iterrows():
        if ',' in str(row['관할구역명']):
            print(f"- {row['관할구역명']}: 여러 구를 관할하는 소방서")
    
    # CSV 파일로 저장
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ 파일 저장 완료: {output_file}")
    
    # 보고서 생성
    report_file = 'dataset/4_select_feature/재난안전취약자정보_feature_selection_보고서.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("재난안전취약자정보 Feature Selection 보고서\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"처리 일시: {pd.Timestamp.now()}\n")
        f.write(f"입력 파일: {input_file}\n")
        f.write(f"출력 파일: {output_file}\n\n")
        f.write("선택된 Features:\n")
        f.write("1. 관할구역명 (구 정보)\n")
        f.write("2. 독거노인가구수\n")
        f.write("3. 고령인구수\n")
        f.write("4. 유아인구수\n")
        f.write("5. 등록장애인수\n")
        f.write("6. 1인가구수\n")
        f.write("7. 화재발생건수\n")
        f.write("8. 관할면적\n\n")
        f.write(f"원본 데이터: {df.shape[0]}개 소방서, {df.shape[1]}개 컬럼\n")
        f.write(f"선택된 데이터: {result_df.shape[0]}개 소방서, {result_df.shape[1]}개 컬럼\n\n")
        f.write("관할구역별 정보:\n")
        f.write(result_df['관할구역명'].value_counts().to_string())
        f.write("\n\n통계 요약:\n")
        f.write(result_df.describe().to_string())
    
    print(f"\n📄 보고서 생성 완료: {report_file}")
    
except Exception as e:
    print(f"❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc() 