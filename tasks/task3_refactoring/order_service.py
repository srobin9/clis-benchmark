from typing import Dict, Any, List

class OrderProcessor:
    """
    모놀리식으로 강하게 결합된 주문 처리 레거시 클래스
    할인 로직, 결제 처리, 알림 발송이 하드코딩되어 있습니다.
    """
    def __init__(self, inventory: Dict[str, int]):
        self.inventory = inventory
        self.sent_notifications: List[str] = []

    def process_order(self, order: Dict[str, Any], user: Dict[str, Any], payment_method: str) -> Dict[str, Any]:
        item_id = order.get("item_id")
        quantity = order.get("quantity", 0)
        base_price = order.get("base_price", 0.0)

        # 1. 재고 검증
        if self.inventory.get(item_id, 0) < quantity:
            return {"status": "FAILED", "reason": "OUT_OF_STOCK"}

        # 2. 강결합된 등급별 할인 계산 로직
        user_tier = user.get("tier", "STANDARD")
        if user_tier == "VIP":
            discount_rate = 0.20
        elif user_tier == "GOLD":
            discount_rate = 0.10
        elif user_tier == "SILVER":
            discount_rate = 0.05
        else:
            discount_rate = 0.0

        subtotal = base_price * quantity
        total_amount = subtotal * (1.0 - discount_rate)

        # 3. 강결합된 결제 수단별 처리
        if payment_method == "CREDIT_CARD":
            fee = 2.5
            payment_status = "SUCCESS"
        elif payment_method == "POINT":
            fee = 0.0
            points = user.get("points", 0)
            if points < total_amount:
                return {"status": "FAILED", "reason": "INSUFFICIENT_POINTS"}
            user["points"] -= total_amount
            payment_status = "SUCCESS"
        else:
            return {"status": "FAILED", "reason": "UNSUPPORTED_PAYMENT_METHOD"}

        final_charge = total_amount + fee

        # 재고 차감
        self.inventory[item_id] -= quantity

        # 알림 발송 기록
        msg = f"Order {order.get('id')} processed: ${final_charge:.2f}"
        self.sent_notifications.append(msg)

        return {
            "status": "SUCCESS",
            "order_id": order.get("id"),
            "final_charge": round(final_charge, 2),
            "discount_applied": round(subtotal * discount_rate, 2),
            "payment_status": payment_status
        }
