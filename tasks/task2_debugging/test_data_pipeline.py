import unittest
from data_pipeline import UserSessionAggregator

class TestUserSessionAggregator(unittest.TestCase):
    def test_filter_consecutive_invalid_events(self):
        aggregator = UserSessionAggregator()
        events = [
            {"type": "invalid1", "timestamp": 10},
            {"type": "invalid2", "timestamp": 20},
            {"type": "click", "timestamp": 30},
            {"type": "unknown", "timestamp": 40},
            {"type": "purchase", "amount": 100, "timestamp": 50},
        ]
        filtered = aggregator.filter_valid_events(events)
        # 연속된 유효하지 않은 이벤트가 모두 정상 필터링되어야 함
        self.assertEqual(len(filtered), 2)
        self.assertEqual([e["type"] for e in filtered], ["click", "purchase"])

    def test_default_argument_mutation_isolation(self):
        agg1 = UserSessionAggregator()
        agg1.valid_event_types.append("custom")

        agg2 = UserSessionAggregator()
        # agg1의 변경이 agg2에 전파되지 않아야 함
        self.assertNotIn("custom", agg2.valid_event_types)

    def test_session_calculation(self):
        aggregator = UserSessionAggregator(session_timeout_seconds=300)
        events = [
            {"type": "click", "timestamp": 0},
            {"type": "view", "timestamp": 100},
            {"type": "purchase", "amount": 50, "timestamp": 200},
            # 200 -> 600 (간격 400 > 300) => 새 세션 분리
            {"type": "click", "timestamp": 600},
            {"type": "purchase", "amount": 150, "timestamp": 750},
        ]
        stats = aggregator.calculate_session_stats(events)
        self.assertEqual(stats["total_sessions"], 2)
        # Session 1: 0~200 (duration: 200)
        # Session 2: 600~750 (duration: 150)
        # Avg: 350 / 2 = 175.0
        self.assertEqual(stats["avg_duration"], 175.0)
        self.assertEqual(stats["total_purchase_amount"], 200)

    def test_empty_events(self):
        aggregator = UserSessionAggregator()
        stats = aggregator.calculate_session_stats([])
        self.assertEqual(stats["total_sessions"], 0)
        self.assertEqual(stats["avg_duration"], 0.0)
        self.assertEqual(stats["total_purchase_amount"], 0)

if __name__ == "__main__":
    unittest.main()
