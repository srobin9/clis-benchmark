import json
import os
from typing import Dict, Any

from ..auth.jwt_handler import TokenManager

class AuthAPI:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "../../config/settings.json")
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        auth_cfg = cfg.get("auth", {})
        self.token_manager = TokenManager(
            secret_key="benchmark-super-secret-key",
            issuer=auth_cfg.get("issuer", "default-issuer"),
            ttl_seconds=auth_cfg.get("token_ttl_seconds", 3600)
        )

    def login(self, user_id: str) -> str:
        return self.token_manager.generate_token(user_id)

    def get_user_profile(self, auth_header: str) -> Dict[str, Any]:
        if not auth_header.startswith("Bearer "):
            raise ValueError("Invalid authorization header")
        token = auth_header.split(" ", 1)[1]
        payload = self.token_manager.verify_token(token)
        return {"user_id": payload.get("sub"), "issuer": payload.get("iss")}
