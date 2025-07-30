#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
화재안전 위험요인 개별 분석
- 인명피해와 화재건수를 각각 분리하여 분석
- 각 그래프를 개별 파일로 저장
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import MinMaxScaler
import platform
import matplotlib.font_manager as fm
import os

# Mac OS용 한글 폰트 설정 (강화)
def setup_korean_font():
    """Mac OS에서 한글 폰트를 확실하게 설정"""
    if platform.system() == 'Darwin':  # Mac OS
        # 모든 사용 가능한 폰트 확인
        available_fonts = [font.name for font in fm.fontManager.ttflist]
        print(f"시스템 폰트 수: {len(available_fonts)}")
        
        # Mac OS 기본 한글 폰트들 우선순위
        korean_fonts = [
            'Apple SD Gothic Neo',  # macOS 기본 한글 폰트
            'AppleGothic',
            'Apple Gothic',
            'Helvetica',
            'Arial Unicode MS',
            'NanumGothic', 
            'NanumMyeongjo',
            'AppleMyungjo'
        ]
        
        selected_font = None
        for font in korean_fonts:
            if font in available_fonts:
                selected_font = font
                print(f"한글 폰트 발견: {font}")
                break
        
        if selected_font:
            # matplotlib 전역 설정
            plt.rcParams['font.family'] = [selected_font, 'sans-serif']
            plt.rcParams['font.sans-serif'] = [selected_font, 'Arial', 'sans-serif']
            
            # seaborn 설정
            import matplotlib
            matplotlib.rcParams['font.family'] = [selected_font, 'sans-serif']
            matplotlib.rcParams['font.sans-serif'] = [selected_font, 'Arial', 'sans-serif']
            
            print(f"✅ 한글 폰트 설정 완료: {selected_font}")
        else:
            # 폴백 설정
            plt.rcParams['font.family'] = ['Apple SD Gothic Neo', 'AppleGothic', 'sans-serif']
            print("⚠️ 폴백 한글 폰트 사용: Apple SD Gothic Neo")
            
        # 폰트 캐시 클리어
        try:
            import matplotlib
            matplotlib.font_manager._get_fontconfig_fonts.cache_clear()
        except AttributeError:
            pass
        
    else:
        plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans', 'Arial', 'sans-serif']
    
    # 마이너스 기호 깨짐 방지
    plt.rcParams['axes.unicode_minus'] = False
    
    # 한글 인코딩 설정
    plt.rcParams['axes.formatter.use_mathtext'] = False
    
    return True

# 한글 폰트 설정 실행
setup_korean_font()

def create_output_directory():
    """결과 저장용 디렉토리 생성"""
    output_dir = 'individual_analysis'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 출력 디렉토리 생성: {output_dir}")
    return output_dir

def analyze_single_target(data, target_var, target_name, target_name_en, factor_map, output_dir):
    """단일 대상 변수에 대한 상관관계 분석"""
    
    components = ['취약연령_정규화', '취약자_정규화', '노후주택_정규화', '구조출동_정규화']
    component_names = ['취약연령밀도', '취약자밀도', '노후주택밀도', '구조출동밀도']
    
    print(f"\n🎯 {target_name} 분석 시작...")
    print("=" * 60)
    
    # 1. 상관관계 계산
    results = []
    
    for component, comp_name in zip(components, component_names):
        # 피어슨 상관계수
        pearson_corr, pearson_p = pearsonr(data[component], data[target_var])
        
        # 스피어만 상관계수
        spearman_corr, spearman_p = spearmanr(data[component], data[target_var])
        
        # 결과 저장
        results.append({
            '위험요인': comp_name,
            '위험요인_영어': factor_map[comp_name],
            '피어슨_상관계수': pearson_corr,
            '피어슨_p값': pearson_p,
            '스피어만_상관계수': spearman_corr,
            '스피어만_p값': spearman_p,
            '유의성': 'Significant' if pearson_p < 0.05 else 'Non-significant',
            '강도': 'Strong' if abs(pearson_corr) > 0.5 else 'Medium' if abs(pearson_corr) > 0.3 else 'Weak'
        })
        
        # 출력
        print(f"📈 {comp_name}")
        print(f"   Pearson: r = {pearson_corr:+.3f} (p = {pearson_p:.3f})")
        print(f"   Spearman: ρ = {spearman_corr:+.3f} (p = {spearman_p:.3f})")
        print(f"   {'⭐ Significant' if pearson_p < 0.05 else '   Non-significant'}")
    
    # 2. DataFrame 생성
    results_df = pd.DataFrame(results)
    
    # 3. CSV 저장
    csv_filename = f"{output_dir}/{target_name_en.lower().replace(' ', '_')}_correlation_matrix.csv"
    results_df.to_csv(csv_filename, index=False, encoding='utf-8')
    print(f"✅ 매트릭스 저장: {csv_filename}")
    
    # 4. 시각화
    create_individual_charts(data, results_df, target_var, target_name, target_name_en, factor_map, output_dir)
    
    return results_df

def create_individual_charts(data, results_df, target_var, target_name, target_name_en, factor_map, output_dir):
    """개별 차트 생성 및 저장"""
    
    # 차트 스타일 설정
    plt.style.use('default')
    
    # 1. 상관계수 막대그래프
    plt.figure(figsize=(10, 6))
    chart_data = results_df.sort_values('피어슨_상관계수', key=abs, ascending=True)
    
    colors = ['red' if x > 0 else 'blue' for x in chart_data['피어슨_상관계수']]
    bars = plt.barh(chart_data['위험요인_영어'], chart_data['피어슨_상관계수'], 
                    color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # 값 표시
    for i, (bar, val, p_val) in enumerate(zip(bars, chart_data['피어슨_상관계수'], chart_data['피어슨_p값'])):
        x_pos = val + (0.03 if val > 0 else -0.03)
        ha = 'left' if val > 0 else 'right'
        significance = '*' if p_val < 0.05 else ''
        plt.text(x_pos, bar.get_y() + bar.get_height()/2, 
                f'{val:+.3f} {significance}', 
                ha=ha, va='center', fontweight='bold', fontsize=12)
    
    plt.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    plt.xlabel('Pearson Correlation Coefficient', fontsize=14, fontweight='bold')
    plt.ylabel('Risk Factors', fontsize=14, fontweight='bold')
    plt.title(f'{target_name_en} Correlation Analysis', fontsize=16, fontweight='bold', pad=20)
    plt.grid(axis='x', alpha=0.3)
    
    # 범례 추가
    plt.text(0.02, 0.98, '* p < 0.05', transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    plt.tight_layout()
    
    # 저장
    bar_filename = f"{output_dir}/{target_name_en.lower().replace(' ', '_')}_correlation_bar.png"
    plt.savefig(bar_filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 막대그래프 저장: {bar_filename}")
    plt.close()
    
    # 2. 가장 강한 상관관계 산점도
    plt.figure(figsize=(8, 6))
    
    # 절댓값 기준으로 가장 강한 상관관계 찾기
    max_corr_idx = results_df['피어슨_상관계수'].abs().idxmax()
    max_row = results_df.iloc[max_corr_idx]
    
    # 해당하는 독립변수 찾기
    component_map = {
        '취약연령밀도': '취약연령_정규화',
        '취약자밀도': '취약자_정규화', 
        '노후주택밀도': '노후주택_정규화',
        '구조출동밀도': '구조출동_정규화'
    }
    
    x_var = component_map[max_row['위험요인']]
    x_data = data[x_var]
    y_data = data[target_var]
    
    # 산점도
    plt.scatter(x_data, y_data, alpha=0.8, s=100, color='orange', 
                edgecolors='black', linewidth=0.8)
    
    # 회귀선
    z = np.polyfit(x_data, y_data, 1)
    p = np.poly1d(z)
    plt.plot(x_data, p(x_data), "r-", alpha=0.8, linewidth=2)
    
    # 상관계수 및 통계 정보 표시
    corr = max_row['피어슨_상관계수']
    p_val = max_row['피어슨_p값']
    r_squared = corr ** 2
    
    stats_text = f'r = {corr:+.3f}\np = {p_val:.3f}\nR² = {r_squared:.1%}'
    plt.text(0.05, 0.95, stats_text, 
             transform=plt.gca().transAxes, fontsize=12, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9),
             verticalalignment='top')
    
    plt.xlabel(f'{max_row["위험요인_영어"]} Density (normalized)', fontsize=14, fontweight='bold')
    plt.ylabel(f'{target_name_en} (normalized)', fontsize=14, fontweight='bold')
    plt.title(f'Strongest Correlation: {max_row["위험요인_영어"]} vs {target_name_en}', 
              fontsize=16, fontweight='bold', pad=20)
    plt.grid(alpha=0.3)
    
    plt.tight_layout()
    
    # 저장
    scatter_filename = f"{output_dir}/{target_name_en.lower().replace(' ', '_')}_scatter.png"
    plt.savefig(scatter_filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 산점도 저장: {scatter_filename}")
    plt.close()
    
    # 3. 상관계수 히트맵 (단일 열)
    plt.figure(figsize=(3, 8))
    
    # 데이터 준비
    heatmap_data = results_df.set_index('위험요인_영어')[['피어슨_상관계수']]
    heatmap_data.columns = [target_name_en]
    
    # 히트맵 생성
    sns.heatmap(heatmap_data, annot=True, cmap='RdBu_r', center=0, 
                fmt='+.3f', cbar_kws={'label': 'Pearson Correlation'},
                linewidths=0.5, square=False,
                annot_kws={'size': 12, 'weight': 'bold'})
    
    plt.title(f'{target_name_en} Risk Factor Heatmap', fontsize=14, fontweight='bold', pad=20)
    plt.ylabel('Risk Factors', fontsize=12, fontweight='bold')
    plt.xlabel('Target Variable', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    # 저장
    heatmap_filename = f"{output_dir}/{target_name_en.lower().replace(' ', '_')}_heatmap.png"
    plt.savefig(heatmap_filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 히트맵 저장: {heatmap_filename}")
    plt.close()

def create_comparison_chart(fire_results, casualty_results, output_dir):
    """화재건수와 인명피해 비교 차트"""
    
    plt.figure(figsize=(12, 8))
    
    # 데이터 준비
    factors = ['VulnAge', 'VulnPop', 'OldHouse', 'Rescue']
    
    fire_corrs = []
    casualty_corrs = []
    
    for factor in factors:
        fire_corr = fire_results[fire_results['위험요인_영어'] == factor]['피어슨_상관계수'].iloc[0]
        casualty_corr = casualty_results[casualty_results['위험요인_영어'] == factor]['피어슨_상관계수'].iloc[0]
        
        fire_corrs.append(fire_corr)
        casualty_corrs.append(casualty_corr)
    
    # 막대그래프
    x = np.arange(len(factors))
    width = 0.35
    
    bars1 = plt.bar(x - width/2, fire_corrs, width, label='Fire Incidents', 
                    alpha=0.8, color='orange', edgecolor='black', linewidth=0.5)
    bars2 = plt.bar(x + width/2, casualty_corrs, width, label='Fire Casualties', 
                    alpha=0.8, color='red', edgecolor='black', linewidth=0.5)
    
    # 값 표시
    for bar, val in zip(bars1, fire_corrs):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + (0.01 if height >= 0 else -0.03),
                f'{val:+.3f}', ha='center', va='bottom' if height >= 0 else 'top', 
                fontweight='bold', fontsize=10)
    
    for bar, val in zip(bars2, casualty_corrs):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + (0.01 if height >= 0 else -0.03),
                f'{val:+.3f}', ha='center', va='bottom' if height >= 0 else 'top', 
                fontweight='bold', fontsize=10)
    
    plt.xlabel('Risk Factors', fontsize=14, fontweight='bold')
    plt.ylabel('Pearson Correlation Coefficient', fontsize=14, fontweight='bold')
    plt.title('Fire Incidents vs Fire Casualties Correlation Comparison', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xticks(x, factors)
    plt.legend(fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    plt.tight_layout()
    
    # 저장
    comparison_filename = f"{output_dir}/fire_incidents_vs_casualties_comparison.png"
    plt.savefig(comparison_filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 비교 차트 저장: {comparison_filename}")
    plt.close()

def main():
    print("🔍 화재안전 위험요인 개별 분석 시작...")
    print("📋 분석 방법: 혼합 접근법")
    print("   - 독립변수: 밀도 기반 (면적으로 정규화)")
    print("   - 종속변수: 절대값 기반 (실제 발생건수/피해)")
    
    # 1. 출력 디렉토리 생성
    output_dir = create_output_directory()
    
    # 2. 데이터 로딩
    print("\n📂 데이터 로딩 중...")
    data = pd.read_csv('correlation_analysis_data.csv', encoding='utf-8')
    print(f"✅ 데이터 로드 완료: {data.shape}")
    print(f"📊 분석 대상: {len(data)}개 구")
    
    # 3. 영어 레이블 매핑
    factor_map = {
        '취약연령밀도': 'VulnAge', 
        '취약자밀도': 'VulnPop', 
        '노후주택밀도': 'OldHouse', 
        '구조출동밀도': 'Rescue'
    }
    
    # 4. 화재발생건수 분석
    fire_results = analyze_single_target(
        data=data,
        target_var='화재발생_절대값_정규화',
        target_name='화재발생건수',
        target_name_en='Fire Incidents',
        factor_map=factor_map,
        output_dir=output_dir
    )
    
    # 5. 인명피해 분석
    casualty_results = analyze_single_target(
        data=data,
        target_var='인명피해_절대값_정규화',
        target_name='인명피해',
        target_name_en='Fire Casualties',
        factor_map=factor_map,
        output_dir=output_dir
    )
    
    # 6. 비교 차트 생성
    print(f"\n📊 비교 차트 생성 중...")
    create_comparison_chart(fire_results, casualty_results, output_dir)
    
    # 7. 전체 결과 매트릭스 저장
    print(f"\n💾 전체 결과 저장 중...")
    
    # 화재발생건수 결과에 대상변수 컬럼 추가
    fire_results_full = fire_results.copy()
    fire_results_full['대상변수'] = 'Fire Incidents'
    
    # 인명피해 결과에 대상변수 컬럼 추가
    casualty_results_full = casualty_results.copy()
    casualty_results_full['대상변수'] = 'Fire Casualties'
    
    # 통합 결과
    combined_results = pd.concat([fire_results_full, casualty_results_full], ignore_index=True)
    combined_filename = f"{output_dir}/combined_correlation_matrix.csv"
    combined_results.to_csv(combined_filename, index=False, encoding='utf-8')
    print(f"✅ 통합 매트릭스 저장: {combined_filename}")
    
    # 8. 요약 통계
    print(f"\n📊 분석 완료 요약:")
    print("=" * 60)
    
    print(f"\n📁 저장된 파일들:")
    print(f"   📄 CSV Files:")
    print(f"      - fire_incidents_correlation_matrix.csv")
    print(f"      - fire_casualties_correlation_matrix.csv") 
    print(f"      - combined_correlation_matrix.csv")
    
    print(f"\n   📊 Chart Files:")
    print(f"      - fire_incidents_correlation_bar.png")
    print(f"      - fire_incidents_scatter.png")
    print(f"      - fire_incidents_heatmap.png")
    print(f"      - fire_casualties_correlation_bar.png")
    print(f"      - fire_casualties_scatter.png")
    print(f"      - fire_casualties_heatmap.png")
    print(f"      - fire_incidents_vs_casualties_comparison.png")
    
    print(f"\n🎯 핵심 발견:")
    
    # 화재발생건수 최고 상관관계
    fire_max_idx = fire_results['피어슨_상관계수'].abs().idxmax()
    fire_max = fire_results.iloc[fire_max_idx]
    print(f"   🔥 Fire Incidents: {fire_max['위험요인_영어']} (r = {fire_max['피어슨_상관계수']:+.3f})")
    
    # 인명피해 최고 상관관계
    casualty_max_idx = casualty_results['피어슨_상관계수'].abs().idxmax()
    casualty_max = casualty_results.iloc[casualty_max_idx]
    print(f"   🏥 Fire Casualties: {casualty_max['위험요인_영어']} (r = {casualty_max['피어슨_상관계수']:+.3f})")
    
    # 유의한 상관관계 개수
    fire_sig_count = len(fire_results[fire_results['피어슨_p값'] < 0.05])
    casualty_sig_count = len(casualty_results[casualty_results['피어슨_p값'] < 0.05])
    
    print(f"\n📈 통계적 유의성:")
    print(f"   🔥 Fire Incidents: {fire_sig_count}/4 significant correlations")
    print(f"   🏥 Fire Casualties: {casualty_sig_count}/4 significant correlations")
    
    print(f"\n✅ 화재안전 위험요인 개별 분석 완료!")
    print(f"📁 모든 결과가 '{output_dir}' 폴더에 저장되었습니다.")

if __name__ == "__main__":
    main() 