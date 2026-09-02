import json
import base64
import hmac
import hashlib
import time
from typing import Dict, Any, Optional

class TokenManager:
    def __init__(self, secret_key: str, issuer: str, ttl_seconds: int = 3600):
        self.secret_key = secret_key.encode("utf-8")
        self.issuer = issuer
        self.ttl_seconds = ttl_seconds

    def generate_token(self, user_id: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        now = int(time.time())
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + self.ttl_seconds,
            "iss": self.issuer
        }
        if extra_claims:
            payload.update(extra_claims)

        h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        p_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        sig = hmac.new(self.secret_key, f"{h_b64}.{p_b64}".encode(), hashlib.sha256).digest()
        s_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
        return f"{h_b64}.{p_b64}.{s_b64}"

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        토큰을 검증하고 페이로드를 반환합니다.
        버그:
        1. 토큰의 issuer ('iss') 검증 누락
        2. 만료 시간('exp') 비교 시 만료 여부를 잘못 판정하거나 서명 검증 오류
        """
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        h_b64, p_b64, s_b64 = parts
        expected_sig = hmac.new(self.secret_key, f"{h_b64}.{p_b64}".encode(), hashlib.sha256).digest()
        # padding 복원
        sig_padding = s_b64 + "=" * (-len(s_b64) % 4)
        actual_sig = base64.urlsafe_b64decode(sig_padding)

        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError("Signature verification failed")

        payload_padding = p_b64 + "=" * (-len(p_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_padding).decode())

        # 버그: 만료 시간 체크가 반대로 되어 있거나 누락
        now = int(time.time())
        if payload.get("exp", 0) > now: # 버그! 만료가 현재시간보다 크면 유효해야 하는데 여기서 Expired 예외를 발생시킴
            raise ValueError("Token has expired")

        return payload
