# Gemini CLI vs Antigravity CLI Benchmark Suite

본 리포지토리는 **Gemini CLI**와 **Antigravity CLI**의 실질적인 성능(Task Success Rate, Latency) 및 비용 효율성(Tokens, Context Cache Utilization, TCO)을 동일한 조건에서 정량적으로 비교·검증하기 위한 벤치마크 테스트 스위트 및 실측 결과 보고서입니다.

최근 추가된 **Gemini 3.7 Flash** 모델을 포함한 **3자 맞비교 벤치마크** 데이터가 포함되어 있습니다.

---

## 1. 벤치마크 3자 실측 요약 (Executive 3-Way Comparison)

* **테스트 환경**: macOS (Apple Silicon M-series), 4대 대표 실무 코딩 과제 기준
* **비교 대상**:
  1. **Gemini CLI (3.5 Flash)**: Google Gemini CLI 기본 엔진
  2. **Antigravity CLI (3.5 Flash)**: 동일 세대 모델 환경에서의 에이전트 성능 비교
  3. **Antigravity CLI (3.7 Flash)**: 차세대 하이브리드 추론(Native Reasoning) 모델 탑재 환경

| 핵심 평가 지표 | (A) Gemini CLI (3.5) | (B) Antigravity CLI (3.5) | (C) Antigravity CLI (3.7) | 3.7 개선 효과 (C vs B) | 3.7 vs Gemini CLI (C vs A) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **태스크 성공률 (Pass@1)** | 50.0% (2/4) | 50.0% (2/4) | **50.0% (2/4)** | 안정성 유지 | 동등 |
| **총 소요 시간 (Latency)** | 278.11초 | 567.18초 | **301.59초** | **46.8% 단축 (265.6s ↓)** | **동등 수준 도달** |
| **과제당 평균 소요 시간** | 69.53초 | 141.79초 | **75.40초** | **46.8% 단축** | 오차 범위 내 근접 |
| **총 소모 토큰량** | 716,218 tokens | 195,157 tokens | **317,389 tokens** | 추론 토큰 반영 | **55.6% 대규모 절감 (39.8만 토큰 ↓)** |
| **컨텍스트 캐싱 적중량** | 590,593 tokens | 1,204,579 tokens | **566,164 tokens** | 효율적 캐시 활용 | 동등 수준 유지 |
| **내재적 추론 (Thinking)** | 지원 불가 (0) | 지원 불가 (0) | **3,341 tokens** | **Native Reasoning 신규 도입** | **질적 차별화** |
| **Task 1 속도 (알고리즘)** | 46.75초 | 302.07초 (타임아웃) | **61.72초** | **79.6% 속도 단축 (타임아웃 해소)** | 14초 차이로 근접 |
| **Task 2 속도 (디버깅)** | 78.48초 | 134.41초 | **62.63초** | **53.4% 속도 단축** | **Gemini CLI보다 20.2% 빠름** |

> **주요 시사점**:
> 1. **타임아웃 완전 해소 및 속도 47% 개선**: Antigravity 3.5에서 발생했던 넓은 범위의 파일 탐색 지연이 Gemini 3.7 Flash의 하이브리드 추론(Thinking) 능력과 결합하면서 **총 실행 시간이 567초에서 301초로 46.8% 단축**되었습니다.
> 2. **Gemini CLI 대비 55.6% 토큰 절감 유지**: Gemini CLI(71.6만 토큰) 대비 **절반도 안 되는 31.7만 토큰**만으로 동일한 작업을 완수하여 높은 비용 효율성을 입증했습니다.

---

## 2. 문서 및 디렉토리 구조

```
clis-benchmark/
├── docs/
│   ├── gemini_vs_antigravity_benchmark_plan.md    # 비교 검증 상세 기획서 (KPI, 방법론)
│   ├── gemini_vs_antigravity_benchmark_results.md # 3.5 Flash 기반 1:1 실측 분석 보고서
│   └── gemini_37_vs_35_benchmark_results.md       # Gemini 3.7 Flash 포함 3자 실측 분석 보고서
├── results/
│   ├── benchmark_comparison_raw.json             # 3.5 Flash 실측 원시 데이터 (JSON)
│   └── benchmark_gemini_37_raw.json              # 3.7 Flash 실측 원시 데이터 (JSON)
├── tasks/
│   ├── .templates/                               # 각 과제의 초기 상태 템플릿
│   ├── task1_algorithm/                          # Task 1: Sliding Window Rate Limiter
│   ├── task2_debugging/                          # Task 2: User Session Aggregator Bug Fix
│   ├── task3_refactoring/                        # Task 3: Order Processor Strategy Pattern
│   └── task4_agentic_tool_use/                   # Task 4: JWT Token Auth Multi-file Project
├── run_comparison_benchmark.py                   # 3.5 Flash 벤치마크 오케스트레이터 러너
├── run_gemini_37_benchmark.py                    # 3.7 Flash 벤치마크 전용 러너
├── analyze.py                                    # 3.5 Flash 결과 분석 스크립트
├── analyze_3way.py                               # 3자 결과 종합 분석 스크립트
├── scenarios.json                                # 벤치마크 시나리오 메타데이터 정의
└── README.md
```

---

## 3. 벤치마크 과제 상세 (Tasks)

1. **Task 1: 알고리즘 구현 (`tasks/task1_algorithm`)**
   - 윈도우 슬라이딩 알고리즘 기반 `SlidingWindowRateLimiter` 구현
   - `allow_request`, `get_remaining_quota` 메서드 완성 및 단위 테스트 통과
2. **Task 2: 디버깅 및 결함 수정 (`tasks/task2_debugging`)**
   - 데이터 집계 파이프라인의 기본 인자 변경(Default argument mutation) 및 연속 중복 필터링 버그 분석 및 수정
3. **Task 3: 전략 패턴 리팩토링 (`tasks/task3_refactoring`)**
   - 모놀리식 `OrderProcessor`를 할인 정책(Strategy) 및 결제 처리기(Processor)로 객체지향 분리
   - 하위 호환성 유지 및 확장성 보장
4. **Task 4: 다중 파일 도구 활용 (`tasks/task4_agentic_tool_use`)**
   - 설정 파일, 라우터, 인증 모듈 간의 의존성을 탐색하여 만료 시간 계산 오류 및 발급자(`iss`) 검증 누락 수정

---

## 4. 벤치마크 재현 및 실행 방법

### 사전 요구사항
* Python 3.10+
* Gemini CLI (`gemini`)
* Antigravity CLI (`agy`)
* Google Cloud Project 설정 (`GOOGLE_CLOUD_PROJECT`)

### 실행 커맨드
```bash
# 1. 3.5 Flash 비교 벤치마크 실행
python3 run_comparison_benchmark.py

# 2. 3.7 Flash 비교 벤치마크 실행
python3 run_gemini_37_benchmark.py

# 3. 3자 종합 비교 통계 분석 및 요약 리포트 출력
python3 analyze_3way.py
```
