# Gemini CLI vs Antigravity CLI Benchmark Suite

본 리포지토리는 **Gemini CLI**와 **Antigravity CLI**의 실질적인 성능(Task Success Rate, Latency) 및 비용 효율성(Tokens, Context Cache Utilization, TCO)을 동일한 조건에서 정량적으로 비교·검증하기 위한 벤치마크 테스트 스위트 및 실측 결과 보고서입니다.

---

## 1. 벤치마크 핵심 실측 요약 (Executive Summary)

* **테스트 환경**: macOS (Apple Silicon M-series), 동일한 기저 엔진 `Gemini 3.5 Flash` 기반
* **평가 과제**: 알고리즘 구현, 디버깅, 객체지향 리팩토링, 다중 파일 도구 활용 (총 4개 과제)

| 핵심 평가 지표 | Gemini CLI | Antigravity CLI | 성능 및 효율성 격차 (Delta) |
| :--- | :---: | :---: | :--- |
| **태스크 성공률 (Pass@1)** | 50.0% (2/4) | **50.0% (2/4)** | 동률 (Task 3, 4 성공) |
| **총 토큰 소모량** | 716,218 tokens | **195,157 tokens** | **-72.8% 절감 (521,061 tokens ↓)** |
| **컨텍스트 캐싱 적중량** | 590,593 tokens | **1,204,579 tokens** | **+103.9% 향상 (2.04배 캐시 활용)** |
| **복합 과제(Task 3) 소요 시간** | 110.02초 | **60.66초** | **44.9% 속도 단축** |
| **복합 과제(Task 3+4) 토큰량** | 355,696 tokens | **95,376 tokens** | **-73.2% 절감 (1/4 수준 소모)** |

> **주요 시사점**:
> 동일한 기저 LLM을 사용함에도 불구하고, Antigravity CLI는 정밀한 컨텍스트 필터링 및 효율적인 프롬프트 캐싱 메커니즘을 통해 **Gemini CLI 대비 72.8% 적은 토큰만으로 동일한 작업을 완수**했습니다. 특히 실무에서 자주 발생하는 아키텍처 리팩토링 작업(Task 3)에서는 작업 소요 시간을 45% 단축시키며 81.8%의 토큰을 절감했습니다.

---

## 2. 문서 및 디렉토리 구조

```
clis-benchmark/
├── docs/
│   ├── gemini_vs_antigravity_benchmark_plan.md    # 비교 검증 상세 기획서 (KPI, 방법론)
│   └── gemini_vs_antigravity_benchmark_results.md # 실측 결과 종합 분석 보고서
├── results/
│   └── benchmark_comparison_raw.json             # 실행별 상세 원시 데이터 (JSON)
├── tasks/
│   ├── .templates/                               # 각 과제의 초기 상태 템플릿
│   ├── task1_algorithm/                          # Task 1: Sliding Window Rate Limiter
│   ├── task2_debugging/                          # Task 2: User Session Aggregator Bug Fix
│   ├── task3_refactoring/                        # Task 3: Order Processor Strategy Pattern
│   └── task4_agentic_tool_use/                   # Task 4: JWT Token Auth Multi-file Project
├── run_comparison_benchmark.py                   # 벤치마크 자동화 오케스트레이터 러너
├── analyze.py                                    # 실측 데이터 분석 및 통계 산출 스크립트
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
# 1. 벤치마크 전수 실행
python3 run_comparison_benchmark.py

# 2. 결과 통계 분석 및 요약 리포트 출력
python3 analyze.py
```

---

## 5. 라이선스 및 크레딧
* 본 벤치마크는 Gemini CLI와 Antigravity CLI의 공정한 비교를 위해 동일한 프롬프트 및 초기화 상태에서 수행되었습니다.
