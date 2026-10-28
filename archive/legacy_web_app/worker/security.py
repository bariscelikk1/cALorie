import base64
import hashlib
import hmac
import json
import os
import time


class SignatureError(ValueError):
    pass


def _decode_part(value: str) -> dict:
    padded = value + "=" * (-len(value) % 4)
    return json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))


def _verify_with_key(token: str, key: str, raw_body: bytes, expected_url: str) -> None:
    parts = token.split(".")
    if len(parts) != 3:
        raise SignatureError("Invalid QStash token")
    header, payload, signature = parts
    expected_signature = base64.urlsafe_b64encode(
        hmac.new(key.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    ).decode().rstrip("=")
    if not hmac.compare_digest(signature.rstrip("="), expected_signature):
        raise SignatureError("Invalid QStash signature")
    claims = _decode_part(payload)
    now = int(time.time())
    if claims.get("iss") != "Upstash" or claims.get("sub") != expected_url:
        raise SignatureError("Invalid QStash claims")
    if now > int(claims.get("exp", 0)) or now < int(claims.get("nbf", now + 1)):
        raise SignatureError("Expired or premature QStash token")
    body_hash = base64.urlsafe_b64encode(hashlib.sha256(raw_body).digest()).decode().rstrip("=")
    if not hmac.compare_digest(str(claims.get("body", "")).rstrip("="), body_hash):
        raise SignatureError("QStash body hash does not match")


def verify_qstash(token: str | None, raw_body: bytes) -> None:
    if not token:
        raise SignatureError("Missing QStash signature")
    expected_url = f"{os.environ['WORKER_PUBLIC_URL'].rstrip('/')}/process"
    keys = [
        os.environ.get("QSTASH_CURRENT_SIGNING_KEY", ""),
        os.environ.get("QSTASH_NEXT_SIGNING_KEY", ""),
    ]
    for key in keys:
        if not key:
            continue
        try:
            _verify_with_key(token, key, raw_body, expected_url)
            return
        except SignatureError:
            pass
    raise SignatureError("QStash signature verification failed")

