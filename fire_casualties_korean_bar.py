#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
인명피해 상관관계 막대그래프 - 한국어 버전
텍스트 겹침 문제 해결
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr
import platform
import matplotlib.font_manager as fm

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

def main():
    print("🔍 인명피해 상관관계 막대그래프 생성 중 (한국어 버전)...")
    
    # 1. 데이터 로딩
    data = pd.read_csv('correlation_analysis_data.csv', encoding='utf-8')
    print(f"✅ 데이터 로드 완료: {data.shape}")
    
    # 2. 상관관계 계산
    components = ['취약연령_정규화', '취약자_정규화', '노후주택_정규화', '구조출동_정규화']
    component_names = ['취약연령밀도', '취약자밀도', '노후주택밀도', '구조출동밀도']
    target_var = '인명피해_절대값_정규화'
    
    results = []
    
    for component, comp_name in zip(components, component_names):
        # 피어슨 상관계수
        pearson_corr, pearson_p = pearsonr(data[component], data[target_var])
        
        # 스피어만 상관계수
        spearman_corr, spearman_p = spearmanr(data[component], data[target_var])
        
        # 결과 저장
        results.append({
            '위험요인': comp_name,
            '피어슨_상관계수': pearson_corr,
            '피어슨_p값': pearson_p,
            '스피어만_상관계수': spearman_corr,
            '스피어만_p값': spearman_p
        })
    
    results_df = pd.DataFrame(results)
    
    # 3. 시각화 (한국어, 개선된 레이아웃)
    plt.figure(figsize=(12, 8))  # 더 큰 크기로 조정
    
    # 데이터 정렬 (절댓값 기준 오름차순)
    chart_data = results_df.sort_values('피어슨_상관계수', key=abs, ascending=True)
    
    # 색상 설정
    colors = ['red' if x > 0 else 'blue' for x in chart_data['피어슨_상관계수']]
    
    # 막대그래프 생성
    bars = plt.barh(chart_data['위험요인'], chart_data['피어슨_상관계수'], 
                    color=colors, alpha=0.7, edgecolor='black', linewidth=0.8, height=0.6)
    
    # 값 표시 (겹침 방지를 위한 개선된 위치 조정)
    for i, (bar, val, p_val) in enumerate(zip(bars, chart_data['피어슨_상관계수'], chart_data['피어슨_p값'])):
        # x축 위치 조정 (더 여유있게)
        if val >= 0:
            x_pos = val + 0.04  # 양수일 때 오른쪽에 여유
            ha = 'left'
        else:
            x_pos = val - 0.04  # 음수일 때 왼쪽에 여유
            ha = 'right'
        
        # y축 위치 (막대 중앙)
        y_pos = bar.get_y() + bar.get_height() / 2
        
        # 유의성 표시
        significance = ' *' if p_val < 0.05 else ''
        
        # 텍스트 표시 (더 큰 폰트)
        plt.text(x_pos, y_pos, f'{val:+.3f}{significance}', 
                ha=ha, va='center', fontweight='bold', fontsize=14,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, edgecolor='none'))
    
    # 기준선
    plt.axvline(x=0, color='black', linestyle='-', alpha=0.4, linewidth=1)
    
    # 축 레이블 및 제목
    plt.xlabel('피어슨 상관계수', fontsize=16, fontweight='bold', labelpad=10)
    plt.ylabel('위험 요인', fontsize=16, fontweight='bold', labelpad=10)
    plt.title('인명피해 예측 요인 상관관계 분석', fontsize=18, fontweight='bold', pad=25)
    
    # 격자
    plt.grid(axis='x', alpha=0.3, linestyle='--')
    
    # 범례 설명
    legend_text = '* p < 0.05 (통계적으로 유의함)'
    plt.text(0.02, 0.98, legend_text, transform=plt.gca().transAxes, 
             fontsize=12, verticalalignment='top', 
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.9))
    
    # x축 범위 조정 (여유 공간 확보)
    x_min = min(chart_data['피어슨_상관계수'].min() - 0.15, -0.2)
    x_max = max(chart_data['피어슨_상관계수'].max() + 0.15, 0.6)
    plt.xlim(x_min, x_max)
    
    # y축 여백 조정
    plt.gca().margins(y=0.1)
    
    # 레이아웃 조정
    plt.tight_layout(pad=2.0)
    
    # 저장
    output_filename = 'individual_analysis/fire_casualties_correlation_bar_korean.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none', pad_inches=0.2)
    print(f"✅ 한국어 막대그래프 저장: {output_filename}")
    
    # 결과 출력
    print(f"\n📊 인명피해 상관관계 분석 결과:")
    print("=" * 50)
    
    for _, row in chart_data.sort_values('피어슨_상관계수', key=abs, ascending=False).iterrows():
        significance = "⭐ 유의함" if row['피어슨_p값'] < 0.05 else "   비유의"
        print(f"{significance} {row['위험요인']:8}: r = {row['피어슨_상관계수']:+.3f} (p = {row['피어슨_p값']:.3f})")
    
    plt.show()
    print(f"\n✅ 인명피해 상관관계 막대그래프 생성 완료!")

if __name__ == "__main__":
    main() 