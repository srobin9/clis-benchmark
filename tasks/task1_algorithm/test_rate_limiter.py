import unittest
from rate_limiter import SlidingWindowRateLimiter

class TestSlidingWindowRateLimiter(unittest.TestCase):
    def test_basic_limit(self):
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=10.0)
        # T = 0.0: 3개 요청 허용
        self.assertTrue(limiter.allow_request("client_a", current_time=0.0))
        self.assertTrue(limiter.allow_request("client_a", current_time=1.0))
        self.assertTrue(limiter.allow_request("client_a", current_time=2.0))
        # 4번째 요청 거절
        self.assertFalse(limiter.allow_request("client_a", current_time=3.0))

    def test_window_sliding_expiry(self):
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=5.0)
        self.assertTrue(limiter.allow_request("user1", current_time=1.0))
        self.assertTrue(limiter.allow_request("user1", current_time=3.0))
        self.assertFalse(limiter.allow_request("user1", current_time=4.0))

        # T = 6.1 -> T = 1.0 요청(6.1 - 5.0 = 1.1 이전) 만료됨
        self.assertTrue(limiter.allow_request("user1", current_time=6.1))
        # 아직 T = 3.0 요청은 유효하므로 총 2개(3.0, 6.1)라 다음은 거절
        self.assertFalse(limiter.allow_request("user1", current_time=7.0))

    def test_multiple_clients_isolated(self):
        limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=5.0)
        self.assertTrue(limiter.allow_request("client_1", current_time=0.0))
        self.assertFalse(limiter.allow_request("client_1", current_time=1.0))
        # client_2는 독립적으로 허용
        self.assertTrue(limiter.allow_request("client_2", current_time=1.0))

    def test_remaining_quota(self):
        limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=10.0)
        self.assertEqual(limiter.get_remaining_quota("user", current_time=0.0), 5)
        limiter.allow_request("user", current_time=0.0)
        limiter.allow_request("user", current_time=1.0)
        self.assertEqual(limiter.get_remaining_quota("user", current_time=2.0), 3)

        # 윈도우 만료 후 쿼터 회복
        self.assertEqual(limiter.get_remaining_quota("user", current_time=12.0), 5)

if __name__ == "__main__":
    unittest.main()
