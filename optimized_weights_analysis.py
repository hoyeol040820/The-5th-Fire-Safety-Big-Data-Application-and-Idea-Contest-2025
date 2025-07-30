# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

def optimize_weights_based_on_correlation():
    """
    상관관계 분석 결과를 바탕으로 최적화된 가중치 적용
    """
    print("🎯 상관관계 기반 가중치 최적화 분석 시작...")
    
    try:
        # 1. 기존 분석 결과 로드
        merged_data = pd.read_csv('correlation_analysis_data.csv')
        print(f"✅ 기존 분석 데이터 로드: {len(merged_data)}개 구")
        
        # 2. 각 구성요소별 상관관계 재계산
        components = ['취약연령_평균', '취약자_평균', '노후주택_평균', '구조출동_평균']
        component_names = ['취약연령층', '재난안전취약자', '노후주택', '구조출동']
        
        correlations = {}
        for comp, name in zip(components, component_names):
            corr, p_val = pearsonr(merged_data[comp], merged_data['인명피해_정규화'])
            correlations[name] = {'corr': corr, 'p_value': p_val, 'abs_corr': abs(corr)}
        
        print(f"\n📊 구성요소별 상관관계:")
        for name, stats in correlations.items():
            print(f"• {name}: r={stats['corr']:+.3f}, p={stats['p_value']:.3f}")
        
        # 3. 다양한 가중치 최적화 방법 적용
        
        # 방법 1: 절댓값 상관계수 비례
        method1_weights = {}
        total_abs_corr = sum([stats['abs_corr'] for stats in correlations.values()])
        for name, stats in correlations.items():
            method1_weights[name] = stats['abs_corr'] / total_abs_corr
        
        # 방법 2: 결정계수(R²) 기반
        method2_weights = {}
        total_r_squared = sum([stats['corr']**2 for stats in correlations.values()])
        for name, stats in correlations.items():
            method2_weights[name] = (stats['corr']**2) / total_r_squared
        
        # 방법 3: 통계적 유의성 반영 (p<0.05면 2배, p<0.1면 1.5배 가중)
        method3_weights = {}
        weighted_corrs = {}
        for name, stats in correlations.items():
            if stats['p_value'] < 0.05:
                weighted_corrs[name] = stats['abs_corr'] * 2.0  # 유의함
            elif stats['p_value'] < 0.1:
                weighted_corrs[name] = stats['abs_corr'] * 1.5  # 거의 유의함
            else:
                weighted_corrs[name] = stats['abs_corr'] * 1.0  # 일반
        
        total_weighted = sum(weighted_corrs.values())
        for name in weighted_corrs:
            method3_weights[name] = weighted_corrs[name] / total_weighted
        
        # 방법 4: 전문가 판단 + 데이터 기반 조합 (추천)
        method4_weights = {
            '노후주택': 0.45,        # 가장 강한 상관관계 + 유의함
            '재난안전취약자': 0.25,   # 두 번째 강한 상관관계
            '취약연령층': 0.20,      # 세 번째 상관관계
            '구조출동': 0.10         # 약한 상관관계이지만 정책적 중요성
        }
        
        # 4. 가중치 비교표 출력
        print(f"\n📋 가중치 최적화 결과 비교:")
        print(f"{'구성요소':^12} | {'기존':^8} | {'방법1':^8} | {'방법2':^8} | {'방법3':^8} | {'추천':^8}")
        print("-" * 70)
        
        original_weights = {'취약연령층': 0.30, '재난안전취약자': 0.30, '노후주택': 0.20, '구조출동': 0.20}
        
        for name in component_names:
            print(f"{name:^12} | {original_weights[name]:^8.1%} | "
                  f"{method1_weights[name]:^8.1%} | {method2_weights[name]:^8.1%} | "
                  f"{method3_weights[name]:^8.1%} | {method4_weights[name]:^8.1%}")
        
        # 5. 새로운 가중치로 종합위험도 재계산
        methods = {
            '기존': original_weights,
            '상관계수비례': method1_weights,
            'R²기반': method2_weights,
            '유의성반영': method3_weights,
            '데이터기반추천': method4_weights
        }
        
        results_comparison = {}
        
        for method_name, weights in methods.items():
            # 새로운 종합위험도 계산
            new_comprehensive = (
                merged_data['취약연령_평균'] * weights['취약연령층'] +
                merged_data['취약자_평균'] * weights['재난안전취약자'] +
                merged_data['노후주택_평균'] * weights['노후주택'] +
                merged_data['구조출동_평균'] * weights['구조출동']
            )
            
            # 새로운 상관관계 계산
            new_corr, new_p = pearsonr(new_comprehensive, merged_data['인명피해_정규화'])
            results_comparison[method_name] = {
                'correlation': new_corr,
                'p_value': new_p,
                'weights': weights
            }
        
        # 6. 결과 비교
        print(f"\n📈 가중치별 상관관계 개선 효과:")
        print(f"{'방법':^15} | {'상관계수':^10} | {'p-value':^10} | {'개선도':^8}")
        print("-" * 50)
        
        baseline_corr = results_comparison['기존']['correlation']
        
        for method, result in results_comparison.items():
            improvement = result['correlation'] - baseline_corr
            print(f"{method:^15} | {result['correlation']:^10.3f} | "
                  f"{result['p_value']:^10.3f} | {improvement:^+8.3f}")
        
        # 7. 최적 가중치 선택 및 적용
        best_method = max(results_comparison.items(), key=lambda x: x[1]['correlation'])
        print(f"\n🏆 최적 가중치 방법: {best_method[0]}")
        print(f"   상관계수: {best_method[1]['correlation']:.3f}")
        print(f"   p-value: {best_method[1]['p_value']:.3f}")
        
        # 8. 최적 가중치로 새로운 종합위험도 계산
        optimal_weights = best_method[1]['weights']
        merged_data['최적_종합위험도'] = (
            merged_data['취약연령_평균'] * optimal_weights['취약연령층'] +
            merged_data['취약자_평균'] * optimal_weights['재난안전취약자'] +
            merged_data['노후주택_평균'] * optimal_weights['노후주택'] +
            merged_data['구조출동_평균'] * optimal_weights['구조출동']
        )
        
        # 9. 시각화
        print(f"\n📊 최적화 결과 시각화 중...")
        
        # Mac 한글 폰트 설정
        import platform
        import matplotlib.font_manager as fm
        
        if platform.system() == 'Darwin':
            available_fonts = [font.name for font in fm.fontManager.ttflist]
            korean_fonts = ['AppleGothic', 'AppleMyungjo', 'NanumGothic', 'NanumMyeongjo']
            
            selected_font = None
            for font in korean_fonts:
                if font in available_fonts:
                    selected_font = font
                    break
            
            if selected_font:
                plt.rcParams['font.family'] = selected_font
            else:
                plt.rcParams['font.family'] = 'AppleGothic'
        
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 기존 vs 최적화 가중치 비교
        ax1.scatter(merged_data['종합위험도_평균'], merged_data['인명피해_정규화'], 
                   alpha=0.6, s=60, color='blue', label='기존 가중치')
        ax1.scatter(merged_data['최적_종합위험도'], merged_data['인명피해_정규화'], 
                   alpha=0.6, s=60, color='red', label='최적 가중치')
        ax1.set_xlabel('종합위험도 점수')
        ax1.set_ylabel('화재인명피해 (정규화)')
        ax1.set_title(f'가중치 최적화 전후 비교\n기존 r={baseline_corr:.3f} → 최적 r={best_method[1]["correlation"]:.3f}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 가중치 비교 막대그래프
        components_kr = ['취약연령층', '재난안전취약자', '노후주택', '구조출동']
        x = np.arange(len(components_kr))
        width = 0.35
        
        original_values = [original_weights[comp] for comp in components_kr]
        optimal_values = [optimal_weights[comp] for comp in components_kr]
        
        ax2.bar(x - width/2, original_values, width, label='기존 가중치', alpha=0.7, color='skyblue')
        ax2.bar(x + width/2, optimal_values, width, label='최적 가중치', alpha=0.7, color='salmon')
        ax2.set_xlabel('구성요소')
        ax2.set_ylabel('가중치')
        ax2.set_title('가중치 최적화 전후 비교')
        ax2.set_xticks(x)
        ax2.set_xticklabels(components_kr, rotation=45)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 구별 순위 변화
        merged_data['기존_순위'] = merged_data['종합위험도_평균'].rank(ascending=False)
        merged_data['최적_순위'] = merged_data['최적_종합위험도'].rank(ascending=False)
        merged_data['순위_변화'] = merged_data['기존_순위'] - merged_data['최적_순위']
        
        colors = ['red' if x > 0 else 'blue' for x in merged_data['순위_변화']]
        ax3.barh(range(len(merged_data)), merged_data['순위_변화'], color=colors, alpha=0.7)
        ax3.set_yticks(range(len(merged_data)))
        ax3.set_yticklabels([gu.replace('구', '') for gu in merged_data['구명']], fontsize=8)
        ax3.set_xlabel('순위 변화 (상승: 빨강, 하락: 파랑)')
        ax3.set_title('구별 위험도 순위 변화')
        ax3.grid(True, alpha=0.3)
        ax3.axvline(x=0, color='black', linewidth=0.8)
        
        # 상관관계 개선 효과
        methods_names = list(results_comparison.keys())
        correlations_values = [results_comparison[method]['correlation'] for method in methods_names]
        colors_bar = ['red' if method == best_method[0] else 'lightblue' for method in methods_names]
        
        ax4.bar(range(len(methods_names)), correlations_values, color=colors_bar, alpha=0.7)
        ax4.set_xticks(range(len(methods_names)))
        ax4.set_xticklabels(methods_names, rotation=45)
        ax4.set_ylabel('상관계수')
        ax4.set_title('가중치 방법별 상관관계 성능')
        ax4.grid(True, alpha=0.3)
        ax4.axhline(y=baseline_corr, color='red', linestyle='--', alpha=0.7, label='기존 성능')
        ax4.legend()
        
        fig.suptitle('상관관계 기반 가중치 최적화 분석 결과', fontsize=16, y=0.98)
        plt.tight_layout()
        plt.subplots_adjust(top=0.93)
        plt.savefig('optimized_weights_analysis.png', dpi=300, bbox_inches='tight')
        print(f"✅ 시각화 저장: optimized_weights_analysis.png")
        
        # 10. 최종 결과 요약
        print(f"\n🎯 가중치 최적화 결과 요약:")
        print("=" * 60)
        print(f"📈 상관관계 개선: {baseline_corr:.3f} → {best_method[1]['correlation']:.3f} "
              f"(+{best_method[1]['correlation'] - baseline_corr:.3f})")
        print(f"📊 최적 가중치:")
        for comp, weight in optimal_weights.items():
            print(f"   • {comp}: {weight:.1%}")
        
        print(f"\n🔝 최적화 후 위험도 상위 10개 구:")
        top_optimized = merged_data.nlargest(10, '최적_종합위험도')[
            ['구명', '최적_종합위험도', '인명피해_소계', '순위_변화']
        ]
        for idx, row in top_optimized.iterrows():
            change_str = f"(순위 {'+' if row['순위_변화'] > 0 else ''}{row['순위_변화']:.0f})" if row['순위_변화'] != 0 else ""
            print(f"   {row['구명']}: {row['최적_종합위험도']:.3f}, "
                  f"인명피해={row['인명피해_소계']:.0f}명 {change_str}")
        
        # 데이터 저장
        merged_data.to_csv('optimized_weights_result.csv', index=False, encoding='utf-8-sig')
        print(f"\n✅ 최적화 결과 저장: optimized_weights_result.csv")
        
        return merged_data, optimal_weights, best_method[1]['correlation']
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None

if __name__ == "__main__":
    print("🎯 상관관계 기반 가중치 최적화")
    print("=" * 60)
    
    result_data, optimal_weights, improved_corr = optimize_weights_based_on_correlation()
    
    if result_data is not None:
        print(f"\n🎉 가중치 최적화 완료!")
        print(f"📊 개선된 상관계수: {improved_corr:.4f}")
        print(f"🎯 최적 가중치: {optimal_weights}")
    else:
        print(f"\n💥 최적화 실패!") 