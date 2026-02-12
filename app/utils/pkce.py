import base64
import secrets
import hashlib


# --- PKCE helpers ---
def create_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)).rstrip(b'=').decode()
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(
        code_verifier.encode()).digest()).rstrip(b'=').decode()
    return code_verifier, code_challenge
