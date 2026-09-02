import time
from typing import Dict, List

class SlidingWindowRateLimiter:
    """
    Sliding Window Rate Limiter
    각 클라이언트(client_id)별로 특정 시간 윈도우(window_seconds) 동안
    허용 가능한 최대 요청 수(max_requests)를 제한하는 클래스입니다.
    """
    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # TODO: 필요한 상태 저장소를 초기화하세요.

    def allow_request(self, client_id: str, current_time: float = None) -> bool:
        """
        주어진 client_id에 대해 요청을 허용할지 여부를 결정합니다.
        - current_time이 주어지지 않으면 time.time()을 사용합니다.
        - 윈도우 기간이 지난 이전 요청 타임스탬프는 제거되어야 합니다.
        - 현재 요청을 포함하여 윈도우 내 요청 수가 max_requests 이하이면 True를 반환하고 타임스탬프를 기록합니다.
        - 초과하면 False를 반환하고 타임스탬프를 기록하지 않습니다.
        """
        # TODO: 슬라이딩 윈도우 알고리즘을 구현하세요.
        raise NotImplementedError("구현이 필요합니다.")

    def get_remaining_quota(self, client_id: str, current_time: float = None) -> int:
        """
        현재 윈도우 내에서 해당 client_id가 추가로 보낼 수 있는 남은 요청 수를 반환합니다.
        """
        # TODO: 잔여 쿼터 계산 로직을 구현하세요.
        raise NotImplementedError("구현이 필요합니다.")
