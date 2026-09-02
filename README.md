# Gemini CLI vs Antigravity CLI Benchmark Suite (신규 전수 재검증 완료)

본 리포지토리는 **Gemini CLI**와 **Antigravity CLI**의 실질적인 성능(Task Success Rate, Latency) 및 비용 효율성(Tokens, Context Cache Utilization, TCO)을 동일한 조건에서 정량적으로 비교·검증하기 위한 벤치마크 테스트 스위트 및 실측 결과 보고서입니다.

테스트 하네스 환경(`PYTHONPATH`)을 완전히 정규화한 후, 4대 실무 개발 과제 x 3개 모델(총 12회 독립 Clean 상태)에 대해 **100% 실시간 전수 재실행을 완료한 실측 데이터**입니다.

---

## 1. 벤치마크 3자 실측 요약 (Executive 3-Way Verified Data)

* **테스트 환경**: macOS (Apple Silicon M-series), 4대 대표 실무 코딩 과제 기준
* **비교 대상**:
  1. **Gemini CLI (3.5 Flash)**: Google Gemini CLI 기본 엔진
  2. **Antigravity CLI (3.5 Flash)**: 동일 세대 모델 환경에서의 에이전트 성능 비교
  3. **Antigravity CLI (3.7 Flash)**: 차세대 하이브리드 추론(Native Reasoning) 모델 탑재 환경

| 핵심 평가 지표 | (A) Gemini CLI (3.5 Flash) | (B) Antigravity CLI (3.5 Flash) | (C) Antigravity CLI (3.7 Flash) | 3.5 vs Gemini (B vs A) | 3.7 vs Gemini (C vs A) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **태스크 완수율 (Pass@1)** | **4/4 (100%)** | **4/4 (100%)** | **4/4 (100%)** | **100% 달성** | **100% 달성** |
| **총 소요 시간 (Latency)** | 264.03초 | 218.86초 | **197.25초** | **17.1% 단축 (45.2s↓)** | **25.3% 단축 (66.8s↓)** |
| **과제당 평균 완료 시간** | 66.01초 | 54.72초 | **49.31초** | **17.1% 단축** | **25.3% 단축 (50초 미만)** |
| **총 소모 토큰량** | 738,366 tokens | **170,318 tokens** | 319,812 tokens | **-76.9% 대폭 절감** | **-56.7% 대규모 절감** |
| **절감된 토큰 수량** | 기준 (0) | **568,048 tokens 절감** | **418,554 tokens 절감** | **Gemini의 23.1%만 소모** | **Gemini의 43.3%만 소모** |
| **컨텍스트 캐싱 적중량** | 615,028 tokens | **683,126 tokens** | 386,920 tokens | 캐시 효율 우수 | 안정적 캐시 유지 |
| **Task 3 리팩토링 토큰** | 233,554 tokens | **36,192 tokens** | 99,975 tokens | **-84.5% 절감** | **-57.2% 절감** |
| **Task 3 리팩토링 시간** | 96.36초 | 54.27초 | **44.16초** | **43.7% 속도 단축** | **54.2% 속도 단축 (최단)** |

> **주요 시사점**:
> 1. **Antigravity 3.5의 압도적 토큰 효율 (-76.9% 절감)**: 세 모델 모두 4개 과제를 100% 통과(Pass@1)했으나, Gemini CLI가 73.8만 토큰을 소모하는 동안 Antigravity 3.5는 단 17.0만 토큰(23.1%)만 소모하여 무려 56.8만 토큰을 절감했습니다.
> 2. **Antigravity 3.7의 압도적 작업 속도 (25.3% 단축)**: Gemini 3.7 Flash를 탑재한 Antigravity는 전체 작업 시간을 197초(과제당 평균 49.3초)로 단축시키며 전 과제를 55초 이내에 끝마쳤습니다.
> 3. **실무 아키텍처 리팩토링(Task 3) 격차**: Gemini CLI가 23.3만 토큰/96초를 소모한 반면, Antigravity 3.7은 44.1초로 2배 이상 빠르게 완수했습니다.

---

## 2. 문서 및 디렉토리 구조

```
clis-benchmark/
├── docs/
│   ├── gemini_vs_antigravity_benchmark_plan.md    # 비교 검증 상세 기획서 (KPI, 방법론)
│   └── gemini_37_vs_35_benchmark_results.md       # 신규 전수 재검증 실측 분석 보고서
├── results/
│   ├── benchmark_fresh_all_raw.json              # 신규 전수 실측 원시 데이터 (12회 전수 실행)
│   ├── benchmark_comparison_raw.json             # 이전 1차 실측 원시 데이터
│   └── benchmark_gemini_37_raw.json              # 이전 2차 실측 원시 데이터
├── tasks/
│   ├── .templates/                               # 각 과제의 초기 상태 템플릿
│   ├── task1_algorithm/                          # Task 1: Sliding Window Rate Limiter
│   ├── task2_debugging/                          # Task 2: User Session Aggregator Bug Fix
│   ├── task3_refactoring/                        # Task 3: Order Processor Strategy Pattern
│   └── task4_agentic_tool_use/                   # Task 4: JWT Token Auth Multi-file Project
├── run_clean_full_benchmark.py                   # 신규 전수 재검증 오케스트레이터 러너
├── analyze_fresh.py                              # 신규 전수 데이터 통계 분석 스크립트
├── create_google_drive_doc.py                    # Google Doc (.docx) 자동 생성 스크립트
├── scenarios.json                                # 벤치마크 시나리오 메타데이터 정의
└── README.md
```

---

## 3. 재현 및 실행 방법
```bash
# 신규 전수 벤치마크 실행 (12개 실행 자동화)
python3 run_clean_full_benchmark.py

# 신규 결과 통계 분석
python3 analyze_fresh.py
```
