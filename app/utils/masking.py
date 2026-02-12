import hashlib
import base64

# --- Mask client secret ---


def mask_client_secret(client_id: str, client_secret: str) -> str:
    normalized_id = client_id.strip().lower()
    hasher = hashlib.sha256()
    hasher.update(f"{client_secret}{normalized_id}".encode("utf-8"))
    return base64.b64encode(hasher.digest()).decode()
