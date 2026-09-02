import unittest
from order_service import OrderProcessor

class TestOrderProcessor(unittest.TestCase):
    def setUp(self):
        self.inventory = {"item_101": 10, "item_102": 2}
        self.processor = OrderProcessor(self.inventory)

    def test_vip_credit_card_order(self):
        order = {"id": "ord_1", "item_id": "item_101", "quantity": 2, "base_price": 100.0}
        user = {"tier": "VIP", "points": 0}
        result = self.processor.process_order(order, user, "CREDIT_CARD")

        self.assertEqual(result["status"], "SUCCESS")
        # subtotal: 200, discount 20% = 160, fee = 2.5 => 162.5
        self.assertEqual(result["final_charge"], 162.5)
        self.assertEqual(result["discount_applied"], 40.0)
        self.assertEqual(self.inventory["item_101"], 8)
        self.assertEqual(len(self.processor.sent_notifications), 1)

    def test_out_of_stock(self):
        order = {"id": "ord_2", "item_id": "item_102", "quantity": 5, "base_price": 50.0}
        user = {"tier": "STANDARD", "points": 0}
        result = self.processor.process_order(order, user, "CREDIT_CARD")

        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(result["reason"], "OUT_OF_STOCK")
        self.assertEqual(self.inventory["item_102"], 2)

    def test_point_payment_success_and_deduction(self):
        order = {"id": "ord_3", "item_id": "item_101", "quantity": 1, "base_price": 100.0}
        user = {"tier": "GOLD", "points": 150}
        result = self.processor.process_order(order, user, "POINT")

        self.assertEqual(result["status"], "SUCCESS")
        # subtotal: 100, discount 10% = 90, fee = 0 => 90
        self.assertEqual(result["final_charge"], 90.0)
        self.assertEqual(user["points"], 60.0)

    def test_point_insufficient(self):
        order = {"id": "ord_4", "item_id": "item_101", "quantity": 1, "base_price": 100.0}
        user = {"tier": "STANDARD", "points": 50}
        result = self.processor.process_order(order, user, "POINT")

        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(result["reason"], "INSUFFICIENT_POINTS")

if __name__ == "__main__":
    unittest.main()
