import unittest
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "mock_project")))

from src.api.routes import AuthAPI
from src.auth.jwt_handler import TokenManager

class TestAuthFlow(unittest.TestCase):
    def setUp(self):
        self.api = AuthAPI()

    def test_successful_login_and_profile_access(self):
        token = self.api.login("user_42")
        auth_header = f"Bearer {token}"
        profile = self.api.get_user_profile(auth_header)
        self.assertEqual(profile["user_id"], "user_42")
        self.assertEqual(profile["issuer"], "gemini-service")

    def test_token_expiration_rejection(self):
        manager = TokenManager(secret_key="benchmark-super-secret-key", issuer="gemini-service", ttl_seconds=-10)
        expired_token = manager.generate_token("user_expired")
        with self.assertRaises(ValueError) as ctx:
            manager.verify_token(expired_token)
        self.assertIn("expired", str(ctx.exception).lower())

    def test_invalid_issuer_rejection(self):
        manager = TokenManager(secret_key="benchmark-super-secret-key", issuer="malicious-service", ttl_seconds=3600)
        invalid_issuer_token = manager.generate_token("attacker")
        with self.assertRaises(ValueError) as ctx:
            self.api.get_user_profile(f"Bearer {invalid_issuer_token}")
        self.assertTrue("issuer" in str(ctx.exception).lower() or "invalid" in str(ctx.exception).lower())

if __name__ == "__main__":
    unittest.main()
