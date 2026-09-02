from typing import List, Dict, Any

class UserSessionAggregator:
    """
    사용자 이벤트 로그를 수집하고 집계하는 파이프라인
    """
    # 버그 1: mutable default argument
    def __init__(self, session_timeout_seconds: int = 300, valid_event_types: List[str] = ["click", "view", "purchase"]):
        self.session_timeout_seconds = session_timeout_seconds
        self.valid_event_types = valid_event_types

    def filter_valid_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # 버그 2: 리스트 순회 중 remove를 호출하여 일부 요소가 스킵되는 버그
        filtered = list(events)
        for event in filtered:
            if event.get("type") not in self.valid_event_types:
                filtered.remove(event)
        return filtered

    def calculate_session_stats(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        사용자별 세션을 분리하고 평균 세션 체류시간(초)과 총 구매액을 계산합니다.
        events는 timestamp 기준 오름차순으로 정렬되어 있다고 가정합니다.
        """
        if not events:
            return {"total_sessions": 0, "avg_duration": 0.0, "total_purchase_amount": 0}

        sessions = []
        current_session_start = events[0]["timestamp"]
        current_session_end = events[0]["timestamp"]
        total_purchase = 0

        for event in events:
            t = event["timestamp"]
            # 버그 3: 세션 타임아웃 경계 조건 판정 오류 (초과가 아니라 미만으로 잘못 비교 또는 부호 오류)
            if t - current_session_end > self.session_timeout_seconds:
                sessions.append(current_session_end - current_session_start)
                current_session_start = t
                current_session_end = t
            else:
                current_session_end = t

            if event.get("type") == "purchase":
                total_purchase += event.get("amount", 0)

        # 마지막 세션 기록 누락 방지
        sessions.append(current_session_end - current_session_start)

        # 버그 4: sessions가 비어있을 경우 ZeroDivisionError 가능성
        avg_duration = sum(sessions) / len(sessions) if sessions else 0.0

        return {
            "total_sessions": len(sessions),
            "avg_duration": round(avg_duration, 2),
            "total_purchase_amount": total_purchase
        }
