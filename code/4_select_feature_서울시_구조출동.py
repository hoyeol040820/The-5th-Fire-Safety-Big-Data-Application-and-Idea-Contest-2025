# -*- coding: utf-8 -*-
import pandas as pd
import os

# 파일 경로 설정
input_file = 'dataset/3_pivot/서울시_구조출동_2023_한강_화재.csv'
output_file = 'dataset/4_select_feature/서울시_구조출동_selected_features.csv'

# 출력 디렉토리 생성
os.makedirs('dataset/4_select_feature', exist_ok=True)

try:
    # CSV 파일 읽기
    df = pd.read_csv(input_file, encoding='utf-8')
    print(f"✅ 파일 읽기 완료: {input_file}")
    print(f"원본 데이터 형태: {df.shape}")
    print(f"원본 컬럼: {list(df.columns)}")
    
    # 데이터 필터링 1: PRCS_RSLT_SE_NM이 "오인신고"가 아닌 데이터
    print(f"\n🔍 필터링 1: PRCS_RSLT_SE_NM != '오인신고'")
    if 'PRCS_RSLT_SE_NM' in df.columns:
        print(f"필터링 전 PRCS_RSLT_SE_NM 분포:")
        print(df['PRCS_RSLT_SE_NM'].value_counts())
        
        df_filtered1 = df[df['PRCS_RSLT_SE_NM'] != '오인신고'].copy()
        print(f"필터링 후 데이터 형태: {df_filtered1.shape}")
        print(f"제거된 오인신고 건수: {df.shape[0] - df_filtered1.shape[0]}")
    else:
        print("⚠️ PRCS_RSLT_SE_NM 컬럼이 없습니다.")
        df_filtered1 = df.copy()
    
    # 데이터 필터링 2: ACDNT_OCRN_PLC_NM이 "도로"가 아닌 데이터
    print(f"\n🔍 필터링 2: ACDNT_OCRN_PLC_NM != '도로'")
    if 'ACDNT_OCRN_PLC_NM' in df_filtered1.columns:
        print(f"필터링 전 ACDNT_OCRN_PLC_NM 분포:")
        acdnt_counts = df_filtered1['ACDNT_OCRN_PLC_NM'].value_counts()
        print(acdnt_counts.head(10))
        
        df_filtered2 = df_filtered1[df_filtered1['ACDNT_OCRN_PLC_NM'] != '도로'].copy()
        print(f"필터링 후 데이터 형태: {df_filtered2.shape}")
        print(f"제거된 도로 관련 건수: {df_filtered1.shape[0] - df_filtered2.shape[0]}")
    else:
        print("⚠️ ACDNT_OCRN_PLC_NM 컬럼이 없습니다.")
        df_filtered2 = df_filtered1.copy()
    
    # 필요한 컬럼만 선택
    selected_columns = [
        'GRNDS_CTPV_NM',  # 발생지역_시도명
        'GRNDS_SGG_NM',   # 발생지역_시군구명
        'DAMG_RGN_LOT',   # 피해지역_경도
        'DAMG_RGN_LAT',   # 피해지역_위도
        'PRCS_RSLT_SE_NM' # 처리결과_구분명
    ]
    
    print(f"\n📊 Feature Selection:")
    print(f"선택할 컬럼: {selected_columns}")
    
    # 컬럼 존재 확인
    missing_columns = [col for col in selected_columns if col not in df_filtered2.columns]
    if missing_columns:
        print(f"⚠️ 누락된 컬럼: {missing_columns}")
        # 존재하는 컬럼만 선택
        selected_columns = [col for col in selected_columns if col in df_filtered2.columns]
    
    # 선택된 컬럼으로 필터링
    result_df = df_filtered2[selected_columns].copy()
    
    # 컬럼명을 더 명확하게 변경
    column_mapping = {
        'GRNDS_CTPV_NM': '발생지역_시도명',
        'GRNDS_SGG_NM': '발생지역_시군구명',
        'DAMG_RGN_LOT': '피해지역_경도',
        'DAMG_RGN_LAT': '피해지역_위도',
        'PRCS_RSLT_SE_NM': '처리결과_구분명'
    }
    
    result_df.columns = [column_mapping.get(col, col) for col in result_df.columns]
    
    # 결과 확인
    print(f"\n📊 최종 결과:")
    print(f"최종 데이터 형태: {result_df.shape}")
    print(f"최종 컬럼: {list(result_df.columns)}")
    
    # 샘플 데이터 출력
    print(f"\n📋 샘플 데이터 (상위 10개):")
    print(result_df.head(10))
    
    # 각 컬럼별 정보 확인
    print(f"\n📈 각 컬럼별 정보:")
    for col in result_df.columns:
        if result_df[col].dtype == 'object':
            print(f"\n{col} 분포:")
            print(result_df[col].value_counts().head(10))
        else:
            print(f"\n{col} 통계:")
            print(result_df[col].describe())
    
    # 결측값 확인
    print(f"\n🔍 결측값 확인:")
    print(result_df.isnull().sum())
    
    # 처리결과별 통계 요약
    print(f"\n📊 처리결과별 통계:")
    result_stats = result_df.groupby('처리결과_구분명').size().sort_values(ascending=False)
    print(result_stats)
    
    # 구별 통계 요약
    print(f"\n🏙️ 구별 통계:")
    gu_stats = result_df.groupby('발생지역_시군구명').size().sort_values(ascending=False)
    print(gu_stats.head(10))
    
    # CSV 파일로 저장
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ 파일 저장 완료: {output_file}")
    
    # 보고서 생성
    report_file = 'dataset/4_select_feature/서울시_구조출동_처리_보고서.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("서울시 구조출동 데이터 필터링 및 Feature Selection 보고서\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"처리 일시: {pd.Timestamp.now()}\n")
        f.write(f"입력 파일: {input_file}\n")
        f.write(f"출력 파일: {output_file}\n\n")
        f.write("처리 과정:\n")
        f.write("1. PRCS_RSLT_SE_NM != '오인신고' 필터링\n")
        f.write("2. ACDNT_OCRN_PLC_NM != '도로' 필터링\n")
        f.write("3. 필요한 컬럼만 선택\n\n")
        f.write("선택된 Features:\n")
        f.write("- 발생지역_시도명 (GRNDS_CTPV_NM)\n")
        f.write("- 발생지역_시군구명 (GRNDS_SGG_NM)\n")
        f.write("- 피해지역_경도 (DAMG_RGN_LOT)\n")
        f.write("- 피해지역_위도 (DAMG_RGN_LAT)\n")
        f.write("- 처리결과_구분명 (PRCS_RSLT_SE_NM)\n\n")
        f.write(f"원본 데이터: {df.shape[0]}개 레코드, {df.shape[1]}개 컬럼\n")
        f.write(f"최종 데이터: {result_df.shape[0]}개 레코드, {result_df.shape[1]}개 컬럼\n\n")
        f.write("필터링 결과:\n")
        f.write(f"- 제거된 오인신고 건수: {df.shape[0] - df_filtered1.shape[0] if 'PRCS_RSLT_SE_NM' in df.columns else 0}\n")
        f.write(f"- 제거된 도로 관련 건수: {df_filtered1.shape[0] - df_filtered2.shape[0] if 'ACDNT_OCRN_PLC_NM' in df_filtered1.columns else 0}\n\n")
        f.write("결측값 정보:\n")
        f.write(result_df.isnull().sum().to_string())
        f.write("\n\n처리결과별 통계:\n")
        f.write(result_stats.to_string())
        f.write("\n\n구별 통계 (상위 10개):\n")
        f.write(gu_stats.head(10).to_string())
    
    print(f"\n📄 보고서 생성 완료: {report_file}")
    
except Exception as e:
    print(f"❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc() 